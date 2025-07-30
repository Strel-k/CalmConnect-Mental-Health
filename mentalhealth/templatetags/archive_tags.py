from django import template

register = template.Library()


@register.filter
def get_risk_level(result):
    # Check if any severity contains 'Severe' or 'Extremely' (case insensitive)
    if (result.depression_severity and 
            'severe' in result.depression_severity.lower() or 
            result.anxiety_severity and 
            'severe' in result.anxiety_severity.lower() or 
            result.stress_severity and 
            'severe' in result.stress_severity.lower()):
        return ('High', '#e74c3c')
    elif (result.depression_severity and 
              'moderate' in result.depression_severity.lower() or 
              result.anxiety_severity and 
              'moderate' in result.anxiety_severity.lower() or 
              result.stress_severity and 
              'moderate' in result.stress_severity.lower()):
        return ('Moderate', '#f39c12')
    else:
        return ('Normal', '#2ecc71')


@register.filter
def get_status_class(status):
    return {
        'completed': 'completed',
        'cancelled': 'cancelled',
        'pending': 'pending',
        'confirmed': 'confirmed'
    }.get(status.lower(), '')