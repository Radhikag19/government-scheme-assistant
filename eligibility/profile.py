from typing import Optional, List
from pydantic import BaseModel


class UserProfile(BaseModel):

    age: Optional[int] = None

    education_level: Optional[str] = None

    course_type: Optional[str] = None

    study_year: Optional[int] = None

    gender: Optional[str] = None

    category: Optional[str] = None

    disability: Optional[bool] = None

    annual_income: Optional[float] = None

    geography: Optional[str] = None

    institution_type: Optional[str] = None

    academic_percentage: Optional[float] = None

    academic_percentile: Optional[float] = None

    special_conditions: Optional[List[str]] = None
