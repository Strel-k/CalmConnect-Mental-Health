from django import template

register = template.Library()

@register.filter(name='get_status_class')
def get_status_class(status):
    """Returns a CSS class based on appointment status"""
    status_map = {
        'completed': 'completed',
        'cancelled': 'cancelled',
        'pending': 'pending',
        'confirmed': 'confirmed'
    }
    return status_map.get(status.lower(), '')

@register.filter(name='get_risk_level')
def get_risk_level(result):
    """Returns risk level and color based on DASS21 scores"""
    max_score = max(result.depression_score, result.anxiety_score, result.stress_score)
    
    if max_score >= 28:  # Extremely severe
        return ("Extremely Severe", "#c0392b")
    elif max_score >= 21:  # Severe
        return ("Severe", "#e74c3c")
    elif max_score >= 14:  # Moderate
        return ("Moderate", "#f39c12")
    elif max_score >= 10:  # Mild
        return ("Mild", "#f1c40f")
    else:  # Normal
        return ("Normal", "#2ecc71")