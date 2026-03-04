"""
Named Entity Recognition using spaCy and Transformers.
"""
import re
import spacy
from transformers import pipeline
from typing import List, Dict

# Regex Patterns
PAN_REGEX = r"[A-Z]{5}[0-9]{4}[A-Z]"
CIN_REGEX = r"L\d{6}[A-Z]{2}\d{4}[A-Z]{3}\d{6}"
GSTIN_REGEX = r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}"

class NERExtractor:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if not downloaded (normally we'd download it in setup)
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self.nlp = spacy.load("en_core_web_sm")
            
        # Add custom rule for LAW
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            patterns = [
                {"label": "LAW", "pattern": [{"lower": "insolvency"}, {"lower": "act"}]},
                {"label": "LAW", "pattern": [{"lower": "npa"}]}
            ]
            ruler.add_patterns(patterns)

        # Load HuggingFace pipeline for better accuracy on ORG/PERSON/LOC
        self.hf_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

    def extract_regex_entities(self, text: str) -> List[Dict]:
        entities = []
        for match in re.finditer(PAN_REGEX, text):
            entities.append({"type": "PAN", "text": match.group()})
        for match in re.finditer(CIN_REGEX, text):
            entities.append({"type": "CIN", "text": match.group()})
        for match in re.finditer(GSTIN_REGEX, text):
            entities.append({"type": "GSTIN", "text": match.group()})
        return entities

    def extract_spacy_entities(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            if ent.label_ in ["MONEY", "DATE", "LAW", "GPE", "LOC"]:
                entities.append({"type": ent.label_, "text": ent.text})
        return entities

    def extract_hf_entities(self, text: str) -> List[Dict]:
        hf_results = self.hf_ner(text)
        entities = []
        for res in hf_results:
            ent_type = res.get("entity_group", "")
            if ent_type in ["ORG", "PER", "LOC"]:
                # Map PER -> PERSON to align with standard naming
                mapped_type = "PERSON" if ent_type == "PER" else ent_type
                entities.append({"type": mapped_type, "text": res.get("word", "")})
        return entities

    def extract_entities(self, text: str) -> List[Dict]:
        regex_ents = self.extract_regex_entities(text)
        spacy_ents = self.extract_spacy_entities(text)
        hf_ents = self.extract_hf_entities(text)
        
        all_ents = regex_ents + spacy_ents + hf_ents
        
        # Deduplicate entities (simple exact match deduplication)
        unique_ents = []
        seen = set()
        for ent in all_ents:
            identifier = f"{ent['type']}_{ent['text']}"
            if identifier not in seen:
                seen.add(identifier)
                unique_ents.append(ent)
                
        return unique_ents

def extract_entities(text: str) -> List[Dict]:
    """
    Main function for module-level access.
    Returns list of { "type": "ORG", "text": "Orbit Holdings Ltd." }
    """
    extractor = NERExtractor()
    return extractor.extract_entities(text)
