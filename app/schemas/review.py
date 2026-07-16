from typing import Literal

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    category: Literal[
        "Incident",
        "Problem",
        "Request",
        "Change",
        "Feedback",
    ]

    priority: Literal[
        "low",
        "medium",
        "high",
    ]

    team: Literal[
        "Billing and Payments",
        "Customer Service",
        "General Inquiry",
        "Human Resources",
        "IT Support",
        "Product Support",
        "Returns and Exchanges",
        "Sales and Pre-Sales",
        "Service Outages and Maintenance",
        "Technical Support",
    ]


class ReviewResponse(BaseModel):
    message: str
    ticket_id: int

class BulkReviewItem(BaseModel):
    ticket_id: int

    category: Literal[
        "Incident",
        "Problem",
        "Request",
        "Change",
        "Feedback",
    ]

    priority: Literal[
        "low",
        "medium",
        "high",
    ]

    team: Literal[
        "Billing and Payments",
        "Customer Service",
        "General Inquiry",
        "Human Resources",
        "IT Support",
        "Product Support",
        "Returns and Exchanges",
        "Sales and Pre-Sales",
        "Service Outages and Maintenance",
        "Technical Support",
    ]