from pydantic import BaseModel
from typing import Optional

class CampaignMetrics(BaseModel):
    campaign_name: str
    channel: str
    ctr_percent: float
    cpc: float
    cost: float
    revenue_attributed: float
    romi_percent: float

class OverallStats(BaseModel):
    total_campaigns: int
    avg_ctr: float
    avg_romi: float
    total_revenue: float