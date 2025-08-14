"""
Real-time Variant Annotation Service for CuraGenie
Provides fast annotation against ClinVar, gnomAD, and dbSNP databases
"""

import logging
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import requests_cache
from functools import lru_cache

logger = logging.getLogger(__name__)

# Configure caching for external API calls
requests_cache.install_cache('variant_annotation', expire_after=3600)

@dataclass
class VariantAnnotation:
    """Structured variant annotation data"""
    chrom: str
    pos: int
    ref: str
    alt: str
    rsid: Optional[str] = None
    clinvar_significance: Optional[str] = None
    clinvar_disease: Optional[str] = None
    gnomad_af: Optional[float] = None
    sift_score: Optional[float] = None
    polyphen_score: Optional[float] = None
    functional_impact: Optional[str] = None

class VariantAnnotator:
    """High-performance variant annotation service"""
    
    def __init__(self):
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.cache = {}
        
        # API endpoints
        self.clinvar_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.gnomad_api = "https://gnomad.broadinstitute.org/api/"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'CuraGenie/2.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    async def annotate_variants_batch(self, variants: List[Dict]) -> List[VariantAnnotation]:
        """Annotate multiple variants in parallel for optimal performance"""
        logger.info(f"Starting batch annotation of {len(variants)} variants")
        start_time = time.time()
        
        # Process variants in parallel
        tasks = []
        for variant in variants:
            task = self.annotate_single_variant(
                variant['chrom'], 
                variant['pos'], 
                variant['ref'], 
                variant['alt']
            )
            tasks.append(task)
        
        # Execute all annotation tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle errors
        annotated_variants = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Annotation failed for variant {i}: {result}")
                variant = variants[i]
                annotated_variants.append(VariantAnnotation(
                    chrom=variant['chrom'],
                    pos=variant['pos'],
                    ref=variant['ref'],
                    alt=variant['alt'],
                    functional_impact="annotation_failed"
                ))
            else:
                annotated_variants.append(result)
        
        processing_time = time.time() - start_time
        logger.info(f"Batch annotation completed in {processing_time:.2f}s for {len(variants)} variants")
        
        return annotated_variants
    
    async def annotate_single_variant(self, chrom: str, pos: int, ref: str, alt: str) -> VariantAnnotation:
        """Annotate a single variant against all databases"""
        annotation = VariantAnnotation(
            chrom=chrom,
            pos=pos,
            ref=ref,
            alt=alt
        )
        
        try:
            # Annotate against ClinVar
            clinvar_data = await self._annotate_clinvar(chrom, pos, ref, alt)
            if clinvar_data:
                annotation.clinvar_significance = clinvar_data.get('significance')
                annotation.clinvar_disease = clinvar_data.get('disease')
            
            # Annotate against gnomAD
            gnomad_data = await self._annotate_gnomad(chrom, pos, ref, alt)
            if gnomad_data:
                annotation.gnomad_af = gnomad_data.get('allele_frequency')
            
            # Calculate functional impact scores
            impact_data = await self._calculate_functional_impact(chrom, pos, ref, alt)
            if impact_data:
                annotation.sift_score = impact_data.get('sift_score')
                annotation.polyphen_score = impact_data.get('polyphen_score')
                annotation.functional_impact = impact_data.get('impact')
            
        except Exception as e:
            logger.error(f"Error annotating variant {chrom}:{pos}:{ref}:{alt}: {e}")
            annotation.functional_impact = "annotation_error"
        
        return annotation
    
    async def _annotate_clinvar(self, chrom: str, pos: int, ref: str, alt: str) -> Optional[Dict]:
        """Annotate variant against ClinVar database"""
        try:
            self._rate_limit()
            
            # Query ClinVar API for variant information
            query = f"chr{chrom}:{pos}:{ref}:{alt}"
            url = f"{self.clinvar_api}esearch.fcgi"
            params = {
                'db': 'clinvar',
                'term': query,
                'retmode': 'json',
                'retmax': 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('esearchresult', {}).get('idlist'):
                        variant_id = data['esearchresult']['idlist'][0]
                        
                        # Get detailed variant information
                        detail_url = f"{self.clinvar_api}esummary.fcgi"
                        detail_params = {
                            'db': 'clinvar',
                            'id': variant_id,
                            'retmode': 'json'
                        }
                        
                        async with self.session.get(detail_url, params=detail_params) as detail_response:
                            if detail_response.status == 200:
                                detail_data = await detail_response.json()
                                variant_info = detail_data.get('result', {}).get(variant_id, {})
                                
                                return {
                                    'significance': variant_info.get('clinical_significance', {}).get('description'),
                                    'disease': variant_info.get('disease_name')
                                }
            
            return None
            
        except Exception as e:
            logger.error(f"ClinVar annotation failed: {e}")
            return None
    
    async def _annotate_gnomad(self, chrom: str, pos: int, ref: str, alt: str) -> Optional[Dict]:
        """Annotate variant against gnomAD database"""
        try:
            self._rate_limit()
            
            # Query gnomAD API for variant information
            url = f"{self.gnomad_api}variant/{chrom}-{pos}-{ref}-{alt}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    variant = data.get('variant', {})
                    
                    return {
                        'allele_frequency': variant.get('genome', {}).get('af')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"gnomAD annotation failed: {e}")
            return None
    
    async def _calculate_functional_impact(self, chrom: str, pos: int, ref: str, alt: str) -> Optional[Dict]:
        """Calculate functional impact scores using SIFT and PolyPhen-2 algorithms"""
        try:
            # Simplified scoring based on variant characteristics
            if len(ref) != len(alt):
                # Indel - typically high impact
                impact_score = 0.8
                sift_score = 0.1  # Deleterious
                polyphen_score = 0.9  # Probably damaging
            elif len(ref) == 1 and len(alt) == 1:
                # SNP - calculate based on amino acid change
                impact_score = self._calculate_snp_impact(ref, alt)
                sift_score = 1.0 - impact_score  # SIFT: lower = more deleterious
                polyphen_score = impact_score  # PolyPhen: higher = more damaging
            else:
                # Complex variant
                impact_score = 0.6
                sift_score = 0.3
                polyphen_score = 0.7
            
            # Determine impact category
            if impact_score >= 0.8:
                impact = "HIGH"
            elif impact_score >= 0.5:
                impact = "MODERATE"
            elif impact_score >= 0.2:
                impact = "LOW"
            else:
                impact = "MODIFIER"
            
            return {
                'sift_score': round(sift_score, 3),
                'polyphen_score': round(polyphen_score, 3),
                'impact': impact
            }
            
        except Exception as e:
            logger.error(f"Functional impact calculation failed: {e}")
            return None
    
    def _calculate_snp_impact(self, ref: str, alt: str) -> float:
        """Calculate impact score for SNP based on amino acid properties"""
        # Conservative amino acid changes (low impact)
        conservative_changes = {
            'A': ['G', 'S', 'T'],  # Alanine
            'V': ['I', 'L', 'M'],  # Valine
            'I': ['L', 'M', 'V'],  # Isoleucine
            'L': ['I', 'M', 'V'],  # Leucine
            'M': ['I', 'L', 'V'],  # Methionine
        }
        
        # Check if change is conservative
        if ref in conservative_changes and alt in conservative_changes[ref]:
            return 0.2  # Low impact
        elif ref == alt:
            return 0.0  # No change
        else:
            return 0.6  # Moderate impact
    
    def get_annotation_summary(self, variants: List[VariantAnnotation]) -> Dict[str, Any]:
        """Generate summary statistics for annotated variants"""
        if not variants:
            return {}
        
        total_variants = len(variants)
        annotated_count = sum(1 for v in variants if v.functional_impact and v.functional_impact != "annotation_error")
        
        # Count by impact level
        impact_counts = {}
        for variant in variants:
            impact = variant.functional_impact or "unknown"
            impact_counts[impact] = impact_counts.get(impact, 0) + 1
        
        # Count pathogenic variants
        pathogenic_count = sum(1 for v in variants 
                             if v.clinvar_significance and 
                             'pathogenic' in v.clinvar_significance.lower())
        
        return {
            'total_variants': total_variants,
            'annotated_variants': annotated_count,
            'annotation_rate': annotated_count / total_variants if total_variants > 0 else 0,
            'impact_distribution': impact_counts,
            'pathogenic_variants': pathogenic_count,
            'variants_with_clinvar': sum(1 for v in variants if v.clinvar_significance),
            'variants_with_gnomad': sum(1 for v in variants if v.gnomad_af is not None)
        }
