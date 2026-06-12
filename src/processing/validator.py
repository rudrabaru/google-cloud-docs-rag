import re
from typing import List, Dict
from src.processing.models import ProcessedDocument


class ProcessingValidator:

    @staticmethod
    def validate_document(
        raw_content: str, processed_blocks: list, doc: ProcessedDocument
    ):
        """Computes before/after statistics and validates preservation."""
        stats = doc.processing_stats

        # Before metrics
        stats.words_before = len(raw_content.split())
        stats.h1_before = len(re.findall(r"^#\s+.*$", raw_content, re.MULTILINE))
        stats.h2_before = len(re.findall(r"^##\s+.*$", raw_content, re.MULTILINE))
        stats.h3_before = len(re.findall(r"^###\s+.*$", raw_content, re.MULTILINE))
        stats.h4_before = len(re.findall(r"^####\s+.*$", raw_content, re.MULTILINE))
        stats.code_blocks_before = (
            len(re.findall(r"^```", raw_content, re.MULTILINE)) // 2
        )
        stats.tables_before = len(re.findall(r"\|[\s\-:]+\|", raw_content))

        # After metrics
        after_content = "\n\n".join(b.content for b in processed_blocks)
        doc.cleaned_markdown = after_content

        stats.words_after = len(after_content.split())
        stats.h1_after = len(re.findall(r"^#\s+.*$", after_content, re.MULTILINE))
        stats.h2_after = len(re.findall(r"^##\s+.*$", after_content, re.MULTILINE))
        stats.h3_after = len(re.findall(r"^###\s+.*$", after_content, re.MULTILINE))
        stats.h4_after = len(re.findall(r"^####\s+.*$", after_content, re.MULTILINE))
        stats.code_blocks_after = (
            len(re.findall(r"^```", after_content, re.MULTILINE)) // 2
        )
        stats.tables_after = len(re.findall(r"\|[\s\-:]+\|", after_content))

        # Retention
        if stats.words_before > 0:
            stats.retention_percentage = (stats.words_after / stats.words_before) * 100
        else:
            stats.retention_percentage = 0.0

    @staticmethod
    def generate_corpus_report(documents: List[ProcessedDocument]) -> Dict:
        """Generates a summary report across all processed documents."""
        total_docs = len(documents)
        if total_docs == 0:
            return {}

        words_before = sum(d.processing_stats.words_before for d in documents)
        words_after = sum(d.processing_stats.words_after for d in documents)

        code_before = sum(d.processing_stats.code_blocks_before for d in documents)
        code_after = sum(d.processing_stats.code_blocks_after for d in documents)

        tables_before = sum(d.processing_stats.tables_before for d in documents)
        tables_after = sum(d.processing_stats.tables_after for d in documents)

        blocks_removed = sum(d.processing_stats.blocks_removed for d in documents)
        blocks_retained = sum(d.processing_stats.blocks_retained for d in documents)

        return {
            "total_documents": total_docs,
            "total_words_before": words_before,
            "total_words_after": words_after,
            "overall_retention": (
                (words_after / words_before * 100) if words_before else 0
            ),
            "code_preservation": {
                "before": code_before,
                "after": code_after,
                "diff": code_after - code_before,
            },
            "table_preservation": {
                "before": tables_before,
                "after": tables_after,
                "diff": tables_after - tables_before,
            },
            "block_statistics": {
                "total_removed": blocks_removed,
                "total_retained": blocks_retained,
                "removal_rate": (
                    (blocks_removed / (blocks_removed + blocks_retained) * 100)
                    if (blocks_removed + blocks_retained) > 0
                    else 0
                ),
            },
        }
