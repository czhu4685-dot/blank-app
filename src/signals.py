"""Task-book premium bands. These are presentation rules, not investment advice."""

from __future__ import annotations

import math


def premium_signal(category: str, premium: float) -> str:
    if premium is None or (isinstance(premium, float) and math.isnan(premium)):
        return "\u6570\u636e\u4e0d\u8db3"
    if category == "\u7eb3\u6307":
        if premium < 0.03:
            return "\u52a0\u4ed3"
        if premium < 0.06:
            return "\u6301\u6709/\u53ef\u4e70"
        if premium < 0.085:
            return "\u8c28\u614e/\u5c11\u4e70"
        if premium < 0.10:
            return "\u51cf\u4ed3"
        return "\u56de\u907f"
    if category == "\u6807\u666e":
        if premium < 0.015:
            return "\u52a0\u4ed3"
        if premium < 0.045:
            return "\u6301\u6709/\u53ef\u4e70"
        if premium < 0.07:
            return "\u51cf\u4ed3"
        return "\u56de\u907f"
    return "\u6682\u672a\u8bbe\u7f6e"
