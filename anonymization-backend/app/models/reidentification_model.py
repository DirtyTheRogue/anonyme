from pydantic import BaseModel
from typing import List


class ReidentificationParams(BaseModel):
    og_tables: List[str]
    anon_tables: List[str]
    ids: List[str]
    count_cols: List[List[str]]
    group_cols: List[List[str]]
    target: List[str]
    exp_features: List[List[str]]
    group_var: List[str]
    og_fusion_table: List[str]
    anon_fusion_table: List[str]
    fusion_columns_to_combine: List[List[str]]
    viz: bool = False
