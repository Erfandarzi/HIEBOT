# utils/extraction_functions.py

from typing import Union, Optional
from pydantic import BaseModel
from openai import OpenAI

class PrimaryOutcome(BaseModel):
    definition: str
    time_window: str
    significance: Union[str, float]

class BayleyScores(BaseModel):
    bayley_ii_cognitive: float
    bayley_iii_cognitive: float
    bayley_iii_language: float
    bayley_ii_cognitive_p_value: float
    bayley_iii_cognitive_p_value: float
    bayley_iii_language_p_value: float

class SampleScores(BaseModel):
    geographic_origin: Optional[Union[float, str]]
    treatment: Optional[Union[float, str]]
    sample_size: Optional[Union[float, str]]
class AdditionalScores(BaseModel):
    authorandyear: Optional[Union[float, str]]
    gmfcs: Optional[Union[float, str]]
    wppsi_iii: Optional[Union[float, str]]
    wisc_iv: Optional[Union[float, str]]

def query_bayley_scores(client: OpenAI, text: str, disease: str):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": f"You are an assistant specialized in extracting detailed scores for studies on HIE. Return the values if those values are existing in the paper. Otherwise return -1"},
            {"role": "user", "content": f"Extract the Bayley II Cognitive, Bayley III Cognitive, and Bayley III Language scores, including values and p-values, from the following study on {disease}: {text}. "}
        ],
        response_format=BayleyScores
    )
    return completion.choices[0].message

def query_sample_scores(client: OpenAI, text: str, disease: str):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": f"You are an assistant specialized in information for studies on {disease}. Extract information on main Author of the study and the year it was published, GMFCS, WPPSI-III, and WISC-IV."},
            {"role": "user", "content": f"Extract information on geographic origin of the study samples, the proposed or studies treatment if any, and the study sample size for the  study on {disease}: {text}.  If the rquired values are mentioned but no specific value is given, provide a brief description of what is stated."}
        ],
        response_format=SampleScores
    )
    return completion.choices[0].message  

def query_primary_outcome(client: OpenAI, text: str, disease: str):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": f"You are an assistant specialized in extracting primary outcome information for studies on {disease}. Extract the definition, time window, and significance of the primary outcome."},
            {"role": "user", "content": f"Extract the primary outcome information from the following study on {disease}: {text}. If information is not available, use 'N/A'."}
        ],
        response_format=PrimaryOutcome
    )
    return completion.choices[0].message

def query_additional_scores(client: OpenAI, text: str, disease: str):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": f"You are an assistant specialized in extracting additional score information for studies on {disease}. Extract information on main Author of the study and the year it was published, GMFCS, WPPSI-III, and WISC-IV."},
            {"role": "user", "content": f"Extract information on Author and year, Gross Motor Functional Classification Scale (GMFCS), Wechsler Preschool and Primary Scale of Intelligence III (WPPSI-III), and Wechsler Intelligence Scale for Children IV (WISC-IV) from the following study on {disease}: {text}. For each score, provide the numeric value if available. If a specific score or value is not mentioned, return null. If a score is mentioned but no specific value is given, provide a brief description of what is stated."}
        ],
        response_format=AdditionalScores
    )
    return completion.choices[0].message    
