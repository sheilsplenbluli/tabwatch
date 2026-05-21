from typing import Dict, List, Optional
from app.models.alert_rule import AlertRule

# In-memory store: {user_id: {rule_id: AlertRule}}
_store: Dict[str, Dict[str, AlertRule]] = {}


def add_rule(rule: AlertRule) -> AlertRule:
    _store.setdefault(rule.user_id, {})[rule.rule_id] = rule
    return rule


def get_rule(user_id: str, rule_id: str) -> Optional[AlertRule]:
    return _store.get(user_id, {}).get(rule_id)


def get_rules_for_user(user_id: str) -> List[AlertRule]:
    return list(_store.get(user_id, {}).values())


def delete_rule(user_id: str, rule_id: str) -> bool:
    user_rules = _store.get(user_id, {})
    if rule_id in user_rules:
        del user_rules[rule_id]
        return True
    return False


def update_rule(rule: AlertRule) -> Optional[AlertRule]:
    if rule.rule_id in _store.get(rule.user_id, {}):
        _store[rule.user_id][rule.rule_id] = rule
        return rule
    return None


def clear_all() -> None:
    _store.clear()


def rule_count() -> int:
    return sum(len(rules) for rules in _store.values())
