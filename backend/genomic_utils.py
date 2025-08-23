"""
Advanced Genomic File Parsing Utilities for CuraGenie

This module provides comprehensive parsing and analysis of genomic files including:
- FASTQ quality control and statistics
- VCF variant annotation and filtering
- Genomic quality metrics
- Real polygenic risk score calculations
"""

import gzip
import logging
import statistics
from typing import Dict, List, Tuple, Optional, Any
from io import BytesIO, StringIO
import re
from collections import defaultdict, Counter
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq

# Try different GC import locations
try:
    from Bio.SeqUtils import gc_fraction as GC
except ImportError:
    try:
        from Bio.SeqUtils.GC import gc_fraction as GC  
    except ImportError:
        # Fallback: calculate GC manually
        def GC(sequence):
            """Calculate GC content manually"""
            seq_str = str(sequence).upper()
            gc_count = seq_str.count('G') + seq_str.count('C')
            return 100.0 * gc_count / len(seq_str) if seq_str else 0.0

logger = logging.getLogger(__name__)

class FastqAnalyzer:
    """Advanced FASTQ file analysis with comprehensive quality metrics"""
    
    def __init__(self):
        self.sequences = []
        self.quality_scores = []
        self.read_lengths = []
        self.gc_contents = []
        
    def parse_fastq(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse FASTQ file and extract comprehensive quality metrics
        """
        try:
            # Handle gzipped files
            if filename.lower().endswith('.gz'):
                file_content = gzip.decompress(file_content)
            
            # Parse sequences using BioPython
            # Convert bytes to string for BioPython parsing
            file_text = file_content.decode('utf-8')
            sequences = list(SeqIO.parse(StringIO(file_text), "fastq"))
            total_sequences = len(sequences)
            
            if total_sequences == 0:
                return {
                    "status": "error",
                    "message": "No valid sequences found in FASTQ file"
                }
            
            logger.info(f"Parsing {total_sequences} sequences from FASTQ file")
            
            # Extract metrics for analysis (use subset for large files)
            sample_size = min(total_sequences, 10000)  # Analyze up to 10k reads
            sample_sequences = sequences[:sample_size]
            
            # Calculate comprehensive metrics
            read_lengths = [len(seq.seq) for seq in sample_sequences]
            gc_contents = [GC(seq.seq) for seq in sample_sequences]
            
            # Quality score analysis
            quality_metrics = self._analyze_quality_scores(sample_sequences)
            
            # Sequence composition analysis
            composition_metrics = self._analyze_sequence_composition(sample_sequences)
            
            # Duplication analysis
            duplication_metrics = self._analyze_duplications(sample_sequences)
            
            # Overall statistics
            metadata = {
                "file_type": "FASTQ",
                "total_sequences": total_sequences,
                "sample_analyzed": sample_size,
                
                # Read length statistics
                "read_length": {
                    "mean": statistics.mean(read_lengths),
                    "median": statistics.median(read_lengths),
                    "min": min(read_lengths),
                    "max": max(read_lengths),
                    "std": statistics.stdev(read_lengths) if len(read_lengths) > 1 else 0
                },
                
                # GC content statistics
                "gc_content": {
                    "mean": statistics.mean(gc_contents),
                    "median": statistics.median(gc_contents),
                    "std": statistics.stdev(gc_contents) if len(gc_contents) > 1 else 0
                },
                
                # Quality metrics
                "quality_metrics": quality_metrics,
                
                # Sequence composition
                "composition_metrics": composition_metrics,
                
                # Duplication metrics
                "duplication_metrics": duplication_metrics,
                
                # Sample sequences (first 3 reads, truncated)
                "sample_sequences": [
                    {
                        "id": seq.id,
                        "sequence": str(seq.seq)[:100],  # First 100 bp
                        "length": len(seq.seq),
                        "gc_content": round(GC(seq.seq), 2)
                    }
                    for seq in sequences[:3]
                ]
            }
            
            logger.info(f"FASTQ analysis complete: {total_sequences} reads, "
                       f"mean length {metadata['read_length']['mean']:.1f}bp, "
                       f"mean GC {metadata['gc_content']['mean']:.1f}%")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing FASTQ file: {e}")
            return {
                "status": "error",
                "message": f"FASTQ parsing failed: {str(e)}"
            }
    
    def _analyze_quality_scores(self, sequences: List) -> Dict[str, Any]:
        """Analyze quality scores across all reads"""
        all_quality_scores = []
        per_base_quality = defaultdict(list)
        
        for seq in sequences:
            if hasattr(seq, 'letter_annotations') and 'phred_quality' in seq.letter_annotations:
                quality_scores = seq.letter_annotations['phred_quality']
                all_quality_scores.extend(quality_scores)
                
                # Per-base quality (for position-specific analysis)
                for pos, qual in enumerate(quality_scores[:100]):  # First 100 positions
                    per_base_quality[pos].append(qual)
        
        if not all_quality_scores:
            return {"status": "no_quality_data"}
        
        # Calculate quality metrics
        mean_quality = statistics.mean(all_quality_scores)
        median_quality = statistics.median(all_quality_scores)
        
        # Quality distribution
        high_quality_bases = sum(1 for q in all_quality_scores if q >= 30)
        medium_quality_bases = sum(1 for q in all_quality_scores if 20 <= q < 30)
        low_quality_bases = sum(1 for q in all_quality_scores if q < 20)
        total_bases = len(all_quality_scores)
        
        # Per-position quality (first 50 positions)
        per_position_quality = {}
        if per_base_quality:  # Only process if we have quality data
            max_pos = max(per_base_quality.keys()) if per_base_quality else 0
            for pos in range(min(50, max_pos + 1)):
                if pos in per_base_quality:
                    per_position_quality[pos] = statistics.mean(per_base_quality[pos])
        
        return {
            "mean_quality": round(mean_quality, 2),
            "median_quality": round(median_quality, 2),
            "quality_distribution": {
                "high_quality_percent": round(100 * high_quality_bases / total_bases, 2),
                "medium_quality_percent": round(100 * medium_quality_bases / total_bases, 2),
                "low_quality_percent": round(100 * low_quality_bases / total_bases, 2)
            },
            "per_position_quality": per_position_quality
        }
    
    def _analyze_sequence_composition(self, sequences: List) -> Dict[str, Any]:
        """Analyze nucleotide composition and overrepresented sequences"""
        all_nucleotides = Counter()
        sequence_counter = Counter()
        
        for seq in sequences:
            sequence_str = str(seq.seq).upper()
            all_nucleotides.update(sequence_str)
            sequence_counter[sequence_str] += 1
        
        total_bases = sum(all_nucleotides.values())
        
        # Nucleotide composition
        composition = {
            base: round(100 * count / total_bases, 2) if total_bases > 0 else 0
            for base, count in all_nucleotides.items()
        }
        
        # Most common sequences (potential contamination or overrepresentation)
        most_common_sequences = [
            {
                "sequence": seq[:50],  # First 50 bp
                "count": count,
                "percentage": round(100 * count / len(sequences), 2)
            }
            for seq, count in sequence_counter.most_common(5)
            if count > 1  # Only show sequences that appear more than once
        ]
        
        return {
            "nucleotide_composition": composition,
            "overrepresented_sequences": most_common_sequences
        }
    
    def _analyze_duplications(self, sequences: List) -> Dict[str, Any]:
        """Analyze sequence duplication levels"""
        sequence_counter = Counter(str(seq.seq) for seq in sequences)
        
        total_sequences = len(sequences)
        unique_sequences = len(sequence_counter)
        duplication_rate = round(100 * (1 - unique_sequences / total_sequences), 2)
        
        # Duplication level distribution
        duplication_levels = Counter(sequence_counter.values())
        
        return {
            "total_sequences": total_sequences,
            "unique_sequences": unique_sequences,
            "duplication_rate_percent": duplication_rate,
            "duplication_levels": dict(duplication_levels)
        }


class VcfAnalyzer:
    """Advanced VCF file analysis with variant annotation and filtering"""
    
    def __init__(self):
        self.variants = []
        
    def parse_vcf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse VCF file and extract comprehensive variant information
        """
        try:
            # Handle gzipped files
            if filename.lower().endswith('.gz'):
                file_content = gzip.decompress(file_content)
            
            # Decode content
            vcf_content = file_content.decode('utf-8')
            lines = vcf_content.split('\n')
            
            # Parse header and metadata
            header_info = self._parse_vcf_header(lines)
            
            # Parse variants
            variant_lines = [line for line in lines 
                           if not line.startswith('#') and line.strip()]
            
            if not variant_lines:
                return {
                    "status": "error",
                    "message": "No variants found in VCF file"
                }
            
            logger.info(f"Parsing {len(variant_lines)} variants from VCF file")
            
            # Analyze variants (use subset for large files)
            sample_size = min(len(variant_lines), 50000)  # Analyze up to 50k variants
            sample_variants = variant_lines[:sample_size]
            
            # Parse and analyze variants
            parsed_variants = []
            chromosome_stats = defaultdict(int)
            variant_type_stats = defaultdict(int)
            quality_scores = []
            
            for line in sample_variants:
                variant_info = self._parse_variant_line(line)
                if variant_info:
                    parsed_variants.append(variant_info)
                    chromosome_stats[variant_info['chromosome']] += 1
                    variant_type_stats[variant_info['variant_type']] += 1
                    if variant_info['quality'] is not None:
                        quality_scores.append(variant_info['quality'])
            
            # Calculate comprehensive statistics
            metadata = {
                "file_type": "VCF",
                "total_variants": len(variant_lines),
                "sample_analyzed": len(parsed_variants),
                "header_info": header_info,
                
                # Chromosome distribution
                "chromosome_distribution": dict(chromosome_stats),
                
                # Variant type distribution
                "variant_type_distribution": dict(variant_type_stats),
                
                # Quality statistics
                "quality_metrics": self._calculate_quality_metrics(quality_scores),
                
                # Genomic regions analysis
                "genomic_regions": self._analyze_genomic_regions(parsed_variants),
                
                # All parsed variants for downstream processing
                "sample_variants": parsed_variants
            }
            
            logger.info(f"VCF analysis complete: {len(variant_lines)} variants, "
                       f"{len(chromosome_stats)} chromosomes")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing VCF file: {e}")
            return {
                "status": "error", 
                "message": f"VCF parsing failed: {str(e)}"
            }
    
    def _parse_vcf_header(self, lines: List[str]) -> Dict[str, Any]:
        """Parse VCF header information"""
        header_info = {
            "format_version": None,
            "reference_genome": None,
            "info_fields": [],
            "format_fields": [],
            "samples": []
        }
        
        for line in lines:
            if line.startswith('##fileformat='):
                header_info["format_version"] = line.split('=', 1)[1]
            elif line.startswith('##reference='):
                header_info["reference_genome"] = line.split('=', 1)[1]
            elif line.startswith('##INFO='):
                # Parse INFO field definitions
                info_match = re.search(r'ID=(\w+)', line)
                if info_match:
                    header_info["info_fields"].append(info_match.group(1))
            elif line.startswith('##FORMAT='):
                # Parse FORMAT field definitions
                format_match = re.search(r'ID=(\w+)', line)
                if format_match:
                    header_info["format_fields"].append(format_match.group(1))
            elif line.startswith('#CHROM'):
                # Parse sample names
                fields = line.split('\t')
                if len(fields) > 9:
                    header_info["samples"] = fields[9:]
                break
        
        return header_info
    
    def _parse_variant_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single variant line from VCF with genotype information"""
        try:
            fields = line.split('\t')
            if len(fields) < 8:
                return None
            
            chrom, pos, variant_id, ref, alt, qual, filter_status, info = fields[:8]
            
            # Parse genotype if available (FORMAT and sample columns)
            genotype = None
            genotype_quality = None
            if len(fields) >= 10:  # Has FORMAT and at least one sample
                format_fields = fields[8].split(':')
                sample_data = fields[9].split(':')
                
                if 'GT' in format_fields and len(sample_data) > format_fields.index('GT'):
                    genotype = sample_data[format_fields.index('GT')]
                
                if 'GQ' in format_fields and len(sample_data) > format_fields.index('GQ'):
                    try:
                        genotype_quality = int(sample_data[format_fields.index('GQ')])
                    except ValueError:
                        genotype_quality = None
            
            # Determine variant type
            variant_type = self._classify_variant(ref, alt)
            
            # Parse INFO field
            info_dict = self._parse_info_field(info)
            
            return {
                "chromosome": chrom,
                "position": int(pos),
                "id": variant_id if variant_id != '.' else None,
                "reference": ref,
                "alternative": alt,
                "quality": float(qual) if qual != '.' else None,
                "filter": filter_status,
                "variant_type": variant_type,
                "info": info_dict,
                "genotype": genotype,
                "genotype_quality": genotype_quality
            }
            
        except Exception as e:
            logger.warning(f"Error parsing variant line: {e}")
            return None
    
    def _classify_variant(self, ref: str, alt: str) -> str:
        """Classify variant type based on REF and ALT alleles"""
        if len(ref) == 1 and len(alt) == 1:
            return "SNV"  # Single nucleotide variant
        elif len(ref) > len(alt):
            return "Deletion"
        elif len(ref) < len(alt):
            return "Insertion"
        else:
            return "Complex"
    
    def _parse_info_field(self, info: str) -> Dict[str, Any]:
        """Parse VCF INFO field"""
        info_dict = {}
        for item in info.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                # Try to convert to appropriate type
                try:
                    if '.' in value:
                        info_dict[key] = float(value)
                    else:
                        info_dict[key] = int(value)
                except ValueError:
                    info_dict[key] = value
            else:
                info_dict[item] = True
        return info_dict
    
    def _calculate_quality_metrics(self, quality_scores: List[float]) -> Dict[str, Any]:
        """Calculate quality score statistics"""
        if not quality_scores:
            return {"status": "no_quality_data"}
        
        return {
            "mean_quality": round(statistics.mean(quality_scores), 2),
            "median_quality": round(statistics.median(quality_scores), 2),
            "min_quality": min(quality_scores),
            "max_quality": max(quality_scores),
            "high_quality_variants": sum(1 for q in quality_scores if q >= 30),
            "total_variants_with_quality": len(quality_scores)
        }
    
    def _analyze_genomic_regions(self, variants: List[Dict]) -> Dict[str, Any]:
        """Analyze distribution of variants across genomic regions"""
        regions = defaultdict(int)
        
        for variant in variants:
            # Simple region classification based on chromosome and position
            chrom = variant['chromosome']
            pos = variant['position']
            
            # Classify into broad genomic regions
            if chrom.startswith('chr'):
                chrom = chrom[3:]  # Remove 'chr' prefix
            
            if chrom in ['X', 'Y']:
                regions['Sex_chromosomes'] += 1
            elif chrom.isdigit():
                chrom_num = int(chrom)
                if 1 <= chrom_num <= 22:
                    regions['Autosomes'] += 1
                else:
                    regions['Other'] += 1
            else:
                regions['Other'] += 1
        
        return dict(regions)


class GenomicQualityController:
    """Quality control and filtering for genomic data"""
    
    @staticmethod
    def assess_fastq_quality(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality of FASTQ data and provide recommendations"""
        quality_assessment = {
            "overall_quality": "Unknown",
            "issues": [],
            "recommendations": [],
            "pass_filters": True
        }
        
        if "quality_metrics" in metadata and "status" not in metadata["quality_metrics"]:
            qual_metrics = metadata["quality_metrics"]
            mean_quality = qual_metrics.get("mean_quality", 0)
            
            # Quality thresholds
            if mean_quality >= 30:
                quality_assessment["overall_quality"] = "Excellent"
            elif mean_quality >= 25:
                quality_assessment["overall_quality"] = "Good"
            elif mean_quality >= 20:
                quality_assessment["overall_quality"] = "Acceptable"
                quality_assessment["recommendations"].append("Consider quality trimming")
            else:
                quality_assessment["overall_quality"] = "Poor"
                quality_assessment["issues"].append("Low overall quality scores")
                quality_assessment["pass_filters"] = False
        
        # Check duplication levels
        if "duplication_metrics" in metadata:
            dup_rate = metadata["duplication_metrics"].get("duplication_rate_percent", 0)
            if dup_rate > 50:
                quality_assessment["issues"].append("High duplication rate")
                quality_assessment["recommendations"].append("Remove duplicates before analysis")
            elif dup_rate > 20:
                quality_assessment["recommendations"].append("Monitor duplication levels")
        
        # Check read length consistency
        if "read_length" in metadata:
            read_len = metadata["read_length"]
            if read_len.get("std", 0) > 10:
                quality_assessment["issues"].append("Variable read lengths")
        
        return quality_assessment
    
    @staticmethod
    def assess_vcf_quality(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality of VCF data and provide recommendations"""
        quality_assessment = {
            "overall_quality": "Unknown",
            "issues": [],
            "recommendations": [],
            "pass_filters": True
        }
        
        if "quality_metrics" in metadata and "status" not in metadata["quality_metrics"]:
            qual_metrics = metadata["quality_metrics"]
            mean_quality = qual_metrics.get("mean_quality", 0)
            
            # Quality thresholds for variants
            if mean_quality >= 100:
                quality_assessment["overall_quality"] = "Excellent"
            elif mean_quality >= 50:
                quality_assessment["overall_quality"] = "Good"
            elif mean_quality >= 20:
                quality_assessment["overall_quality"] = "Acceptable"
                quality_assessment["recommendations"].append("Consider quality filtering")
            else:
                quality_assessment["overall_quality"] = "Poor"
                quality_assessment["issues"].append("Low variant quality scores")
                quality_assessment["pass_filters"] = False
        
        # Check variant density
        total_variants = metadata.get("total_variants", 0)
        if total_variants < 1000:
            quality_assessment["issues"].append("Low variant count")
        elif total_variants > 10000000:
            quality_assessment["recommendations"].append("Large variant set - consider filtering")
        
        return quality_assessment


# Improved PRS calculation framework
class PolygeneticRiskCalculator:
    """
    Real polygenic risk score calculation framework
    Note: This is still simplified but much more realistic than hash-based scoring
    """
    
    # Example SNP weights for common diseases (simplified example)
    DISEASE_SNP_WEIGHTS = {
        "diabetes": {
            # These would be real SNP IDs and their effect sizes from GWAS
            "rs7903146": 0.34,  # TCF7L2 - strong diabetes association
            "rs12255372": 0.29,  # TCF7L2
            "rs1801282": -0.14,  # PPARG
            "rs5219": 0.08,     # KCNJ11
            "rs13266634": 0.11,  # SLC30A8
        },
        "alzheimer": {
            "rs429358": 1.12,   # APOE e4 allele - very strong association
            "rs7412": -0.68,    # APOE e2 allele - protective
            "rs11136000": 0.15, # CLU
            "rs3851179": 0.09,  # PICALM
        },
        "heart_disease": {
            "rs599839": 0.29,   # SORT1/CELSR2/PSRC1
            "rs17465637": 0.29, # MIA3
            "rs6922269": 0.25,  # MTHFD1L
            "rs1333049": 0.21,  # CDKN2A/CDKN2B
        }
    }
    
    def calculate_prs(self, variants: List[Dict], disease_type: str) -> Dict[str, Any]:
        """
        Calculate polygenic risk score based on variant data with proper genotype scoring
        """
        try:
            disease_snps = self.DISEASE_SNP_WEIGHTS.get(disease_type.lower(), {})
            
            logger.info(f"Calculating PRS for {disease_type} with {len(variants)} variants")
            logger.info(f"Looking for {len(disease_snps)} disease-associated SNPs: {list(disease_snps.keys())}")
            
            # Look for disease-associated variants in the user's data
            found_variants = {}
            prs_contributions = []
            
            for variant in variants:
                variant_id = variant.get('id')
                genotype = variant.get('genotype', '0/1')  # Default to heterozygous
                
                if variant_id and variant_id in disease_snps:
                    logger.info(f"Found disease SNP: {variant_id} with genotype {genotype}")
                    
                    # Calculate contribution based on genotype
                    weight = disease_snps[variant_id]
                    
                    # Real genotype scoring based on actual genotype
                    genotype_score = self._calculate_genotype_score(genotype, weight)
                    
                    contribution = weight * genotype_score
                    prs_contributions.append(contribution)
                    found_variants[variant_id] = {
                        "weight": weight,
                        "genotype": genotype,
                        "genotype_score": genotype_score,
                        "contribution": contribution,
                        "chromosome": variant.get('chromosome'),
                        "position": variant.get('position')
                    }
            
            logger.info(f"Found {len(found_variants)} matching SNPs with contributions: {[v['contribution'] for v in found_variants.values()]}")
            
            # Calculate final PRS
            raw_prs = sum(prs_contributions) if prs_contributions else 0
            
            # If no matching SNPs found, use population-based fallback
            if len(found_variants) == 0:
                logger.info(f"No matching SNPs found, using population-based scoring")
                return self._calculate_population_based_score(variants, disease_type)
            
            # Normalize to 0-1 scale based on typical PRS distributions
            # This is a simplified normalization - real systems use population percentiles
            if disease_type.lower() == 'diabetes':
                # For diabetes, typical PRS range is -1 to +2
                normalized_prs = max(0.0, min(1.0, (raw_prs + 1) / 3))
            elif disease_type.lower() == 'alzheimer':
                # For Alzheimer's, APOE has large effects
                normalized_prs = max(0.0, min(1.0, (raw_prs + 1) / 4))
            else:
                # General normalization
                normalized_prs = max(0.0, min(1.0, (raw_prs + 2) / 4))
            
            return {
                "disease_type": disease_type,
                "score": normalized_prs,  # Use 'score' to match database schema
                "raw_prs": raw_prs,
                "variants_used": len(found_variants),
                "total_possible_variants": len(disease_snps),
                "confidence": min(1.0, len(found_variants) / max(1, len(disease_snps))),
                "contributing_variants": found_variants,
                "method": "snp_based",
                "interpretation": self._interpret_prs_score(normalized_prs)
            }
            
        except Exception as e:
            logger.error(f"Error calculating PRS: {e}")
            return {
                "status": "error",
                "message": f"PRS calculation failed: {str(e)}"
            }
    
    def _calculate_population_based_score(self, variants: List[Dict], disease_type: str) -> Dict[str, Any]:
        """Fallback PRS calculation based on overall variant burden"""
        try:
            # Use variant characteristics to estimate risk
            variant_count = len(variants)
            
            # Simple scoring based on variant density and types
            snv_count = sum(1 for v in variants if v.get('variant_type') == 'SNV')
            indel_count = variant_count - snv_count
            
            # Population-based scoring (very simplified)
            base_score = 0.5  # Population average
            
            # Adjust based on variant burden
            if variant_count > 5000000:  # High variant count
                adjustment = 0.1
            elif variant_count < 1000000:  # Low variant count
                adjustment = -0.1
            else:
                adjustment = 0
            
            # Disease-specific adjustments
            disease_adjustments = {
                "diabetes": 0.08,
                "alzheimer": 0.05,
                "heart_disease": 0.06
            }
            
            disease_adj = disease_adjustments.get(disease_type.lower(), 0)
            final_score = max(0, min(1, base_score + adjustment + disease_adj))
            
            return {
                "disease_type": disease_type,
                "method": "population_based",
                "normalized_prs": final_score,
                "total_variants": variant_count,
                "snv_count": snv_count,
                "indel_count": indel_count,
                "interpretation": self._interpret_prs_score(final_score)
            }
            
        except Exception as e:
            logger.error(f"Error in population-based PRS calculation: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_genotype_score(self, genotype: str, snp_weight: float) -> float:
        """Calculate genotype score based on actual genotype and SNP weight"""
        try:
            # Handle different genotype formats
            if '/' in genotype:
                alleles = genotype.split('/')
            elif '|' in genotype:
                alleles = genotype.split('|')
            else:
                logger.warning(f"Unknown genotype format: {genotype}")
                return 0.5  # Default to heterozygous effect
            
            # Count risk alleles (assume '1' is the risk allele)
            risk_allele_count = sum(1 for allele in alleles if allele == '1')
            
            # Genotype scoring:
            # 0/0 (homozygous reference): 0 copies of risk allele
            # 0/1 or 1/0 (heterozygous): 1 copy of risk allele
            # 1/1 (homozygous alternate): 2 copies of risk allele
            
            if risk_allele_count == 0:
                # No risk alleles - reference genotype
                return 0.0
            elif risk_allele_count == 1:
                # One risk allele - heterozygous effect
                return 1.0
            elif risk_allele_count == 2:
                # Two risk alleles - homozygous effect (typically 2x heterozygous)
                return 2.0
            else:
                logger.warning(f"Unexpected risk allele count: {risk_allele_count}")
                return 1.0
                
        except Exception as e:
            logger.warning(f"Error calculating genotype score for {genotype}: {e}")
            return 1.0  # Default to heterozygous effect
    
    def _interpret_prs_score(self, score: float) -> str:
        """Provide interpretation of PRS score"""
        if score >= 0.8:
            return "Very High Risk"
        elif score >= 0.6:
            return "High Risk"
        elif score >= 0.4:
            return "Moderate Risk"
        elif score >= 0.2:
            return "Low Risk"
        else:
            return "Very Low Risk"


# Main genomic processor class
class GenomicProcessor:
    """Main class for processing genomic files with comprehensive analysis"""
    
    def __init__(self):
        self.fastq_analyzer = FastqAnalyzer()
        self.vcf_analyzer = VcfAnalyzer()
        self.quality_controller = GenomicQualityController()
        self.prs_calculator = PolygeneticRiskCalculator()
    
    def process_genomic_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process genomic file and return comprehensive analysis
        """
        try:
            # Determine file type
            file_extension = filename.lower().split('.')
            if file_extension[-1] == 'gz':
                file_type = file_extension[-2] if len(file_extension) > 1 else 'unknown'
            else:
                file_type = file_extension[-1]
            
            logger.info(f"Processing genomic file: {filename} (type: {file_type})")
            
            # Route to appropriate parser
            if file_type in ['fastq', 'fq']:
                metadata = self.fastq_analyzer.parse_fastq(file_content, filename)
                if "status" not in metadata or metadata["status"] != "error":
                    metadata["quality_assessment"] = self.quality_controller.assess_fastq_quality(metadata)
                
            elif file_type == 'vcf':
                metadata = self.vcf_analyzer.parse_vcf(file_content, filename)
                if "status" not in metadata or metadata["status"] != "error":
                    metadata["quality_assessment"] = self.quality_controller.assess_vcf_quality(metadata)
                
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported file format: {file_type}"
                }
            
            # Add processing metadata
            metadata.update({
                "filename": filename,
                "processing_timestamp": __import__('time').time(),
                "processor_version": "CuraGenie_v2.0_Advanced"
            })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing genomic file {filename}: {e}")
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}"
            }
    
    def calculate_polygenic_risk_score(self, genomic_metadata: Dict[str, Any], 
                                     disease_type: str) -> Dict[str, Any]:
        """
        Calculate polygenic risk score from processed genomic data
        """
        try:
            # Extract variants from metadata
            if genomic_metadata.get("file_type") == "VCF":
                variants = genomic_metadata.get("sample_variants", [])
                return self.prs_calculator.calculate_prs(variants, disease_type)
            else:
                return {
                    "status": "error",
                    "message": "PRS calculation requires VCF file with variant data"
                }
                
        except Exception as e:
            logger.error(f"Error calculating PRS: {e}")
            return {
                "status": "error",
                "message": f"PRS calculation failed: {str(e)}"
            }
