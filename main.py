from fastapi import FastAPI, HTTPException
from typing import List
from app.database import get_db_connection
from app.schemas import CampaignMetrics, OverallStats

app = FastAPI(
    title="Marketing Analytics API",
    description="Микросервис для отдачи маркетинговых метрик (ROMI, CTR) из DWH. Pet-проект.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Проверка живости сервиса и БД."""
    try:
        conn, cur = get_db_connection()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/api/v1/campaigns/top", response_model=List[CampaignMetrics])
def get_top_campaigns(limit: int = 10):
    """Возвращает топ-N кампаний по ROMI."""
    conn, cur = get_db_connection()
    try:
        query = """
            SELECT campaign_name, channel, ctr_percent, cpc, cost, revenue_attributed, romi_percent
            FROM public.marketing_metrics
            ORDER BY romi_percent DESC
            LIMIT %s;
        """
        cur.execute(query, (limit,))
        results = cur.fetchall()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/v1/stats/overall", response_model=OverallStats)
def get_overall_stats():
    """Возвращает общую статистику по всем кампаниям."""
    conn, cur = get_db_connection()
    try:
        query = """
            SELECT 
                COUNT(*) as total_campaigns,
                AVG(ctr_percent) as avg_ctr,
                AVG(romi_percent) as avg_romi,
                SUM(revenue_attributed) as total_revenue
            FROM public.marketing_metrics
            WHERE romi_percent > -100;
        """
        cur.execute(query)
        result = cur.fetchone()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/v1/campaigns/by-channel/{channel}", response_model=List[CampaignMetrics])
def get_campaigns_by_channel(channel: str):
    """Возвращает кампании по конкретному каналу (Telegram, VK, Email, Google Ads)."""
    conn, cur = get_db_connection()
    try:
        query = """
            SELECT campaign_name, channel, ctr_percent, cpc, cost, revenue_attributed, romi_percent
            FROM public.marketing_metrics
            WHERE channel ILIKE %s
            ORDER BY romi_percent DESC;
        """
        cur.execute(query, (f"%{channel}%",))
        results = cur.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail=f"Канал '{channel}' не найден")
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()