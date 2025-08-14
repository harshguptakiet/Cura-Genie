"""
Simplified Variant Annotation Service
Works with minimal dependencies (no numpy/pandas)
"""

import json
import asyncio
import aiohttp
import requests_cache
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure requests cache for external API calls
requests_cache.install_cache('variant_cache', expire_after=3600)  # 1 hour cache

@dataclass
class VariantAnnotation:
    """Simplified variant annotation data structure"""
    chrom: str
    pos: int
    ref: str
    alt: str
    clinvar_significance: Optional[str] = None
    gnomad_frequency: Optional[float] = None
    functional_impact: Optional[str] = None
    disease_association: Optional[str] = None
    evidence_level: Optional[str] = None

class SimpleVariantAnnotator:
    """Simplified variant annotator without numpy/pandas dependencies"""
    
    def __init__(self):
        self.session = None
        self.clinvar_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.gnomad_base_url = "https://gnomad.broadinstitute.org/api/"
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def annotate_variants_batch(self, variants: List[Dict[str, Any]]) -> List[VariantAnnotation]:
        """Annotate a batch of variants"""
        annotations = []
        
        for variant in variants:
            annotation = await self._annotate_single_variant(variant)
            annotations.append(annotation)
            
        return annotations
    
    async def _annotate_single_variant(self, variant: Dict[str, Any]) -> VariantAnnotation:
        """Annotate a single variant"""
        # Extract basic variant information
        chrom = variant.get('chrom', 'unknown')
        pos = variant.get('pos', 0)
        ref = variant.get('ref', 'N')
        alt = variant.get('alt', 'N')
        
        # Create base annotation
        annotation = VariantAnnotation(
            chrom=chrom,
            pos=pos,
            ref=ref,
            alt=alt
        )
        
        # Annotate with ClinVar data
        try:
            clinvar_data = await self._annotate_clinvar(chrom, pos, ref, alt)
            if clinvar_data:
                annotation.clinvar_significance = clinvar_data.get('significance')
                annotation.disease_association = clinvar_data.get('disease')
                annotation.evidence_level = clinvar_data.get('evidence_level')
        except Exception as e:
            print(f"ClinVar annotation failed: {e}")
        
        # Annotate with gnomAD frequency
        try:
            gnomad_freq = await self._annotate_gnomad(chrom, pos, ref, alt)
            if gnomad_freq is not None:
                annotation.gnomad_frequency = gnomad_freq
        except Exception as e:
            print(f"gnomAD annotation failed: {e}")
        
        # Calculate functional impact
        try:
            annotation.functional_impact = self._calculate_functional_impact(ref, alt)
        except Exception as e:
            print(f"Functional impact calculation failed: {e}")
        
        return annotation
    
    async def _annotate_clinvar(self, chrom: str, pos: int, ref: str, alt: str) -> Optional[Dict[str, Any]]:
        """Annotate variant with ClinVar data"""
        if not self.session:
            return None
            
        try:
            # Simplified ClinVar query - in real implementation, you'd use proper API
            # For now, return mock data based on variant characteristics
            if len(ref) != len(alt):
                # Indel variant
                return {
                    'significance': 'uncertain_significance',
                    'disease': 'genetic_variant',
                    'evidence_level': 'limited'
                }
            elif len(ref) == 1 and len(alt) == 1:
                # SNP variant
                if ref in 'AT' and alt in 'GC':
                    return {
                        'significance': 'benign',
                        'disease': 'common_variant',
                        'evidence_level': 'strong'
                    }
                else:
                    return {
                        'significance': 'uncertain_significance',
                        'disease': 'genetic_variant',
                        'evidence_level': 'moderate'
                    }
            else:
                return {
                    'significance': 'uncertain_significance',
                    'disease': 'genetic_variant',
                    'evidence_level': 'limited'
                }
        except Exception as e:
            print(f"ClinVar annotation error: {e}")
            return None
    
    async def _annotate_gnomad(self, chrom: str, pos: int, ref: str, alt: str) -> Optional[float]:
        """Annotate variant with gnomAD frequency data"""
        if not self.session:
            return None
            
        try:
            # Simplified gnomAD frequency calculation
            # In real implementation, you'd query the gnomAD API
            import random
            # Mock frequency based on variant type
            if len(ref) != len(alt):
                # Indel - usually rare
                return random.uniform(0.0001, 0.01)
            elif len(ref) == 1 and len(alt) == 1:
                # SNP - can be common or rare
                if random.random() < 0.3:  # 30% chance of being common
                    return random.uniform(0.01, 0.5)
                else:
                    return random.uniform(0.0001, 0.01)
            else:
                return random.uniform(0.0001, 0.01)
        except Exception as e:
            print(f"gnomAD annotation error: {e}")
            return None
    
    def _calculate_functional_impact(self, ref: str, alt: str) -> str:
        """Calculate simplified functional impact"""
        try:
            if len(ref) != len(alt):
                if len(ref) > len(alt):
                    return "deletion"
                else:
                    return "insertion"
            elif len(ref) == 1 and len(alt) == 1:
                # Simple transition/transversion logic
                purines = {'A', 'G'}
                pyrimidines = {'C', 'T'}
                
                if (ref in purines and alt in purines) or (ref in pyrimidines and alt in pyrimidines):
                    return "transition"
                else:
                    return "transversion"
            else:
                return "complex"
        except Exception as e:
            print(f"Functional impact calculation error: {e}")
            return "unknown"

# Standalone function for testing
async def test_annotation():
    """Test the variant annotation service"""
    annotator = SimpleVariantAnnotator()
    
    # Test variants
    test_variants = [
        {'chrom': 'chr1', 'pos': 1000, 'ref': 'A', 'alt': 'T'},
        {'chrom': 'chr2', 'pos': 2000, 'ref': 'AT', 'alt': 'A'},
        {'chrom': 'chr3', 'pos': 3000, 'ref': 'C', 'alt': 'G'}
    ]
    
    async with annotator:
        annotations = await annotator.annotate_variants_batch(test_variants)
        
        for i, annotation in enumerate(annotations):
            print(f"Variant {i+1}:")
            print(f"  Position: {annotation.chrom}:{annotation.pos}")
            print(f"  Change: {annotation.ref} -> {annotation.alt}")
            print(f"  ClinVar: {annotation.clinvar_significance}")
            print(f"  gnomAD: {annotation.gnomad_frequency}")
            print(f"  Impact: {annotation.functional_impact}")
            print()

if __name__ == "__main__":
    asyncio.run(test_annotation())
