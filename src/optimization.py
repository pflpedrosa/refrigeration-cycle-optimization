import pandas as pd
import copy
from cycles import calculate_basic_cycle, calculate_two_evaporators_cycle

def determine_if_reached_threshold(value, lower, upper):
    reached_threshold = 0
    if value <= lower:
        reached_threshold = 1
        value = lower
    elif value >= upper:
        reached_threshold = 1
        value = upper  
    return value, reached_threshold

def calculate_next_x_two_evaporators_cycle(input_values, x, y, current_cycle, delta, alpha, lower_threshold, upper_threshold):
    current_x = input_values[x]
    input_values_x = copy.copy(input_values)
    input_values_x[x] += delta
    gradient_cycle_x = calculate_two_evaporators_cycle(input_values_x)
    gradient_x = (gradient_cycle_x[y] - current_cycle[y]) / delta
    next_x = current_x + alpha * gradient_x
    next_x, reached_threshold_x = determine_if_reached_threshold(next_x, lower_threshold, upper_threshold)
    return next_x, reached_threshold_x

def calculate_next_all_two_evaporators_cycle(input_values, y, delta, alpha):
      
    current_cycle = calculate_two_evaporators_cycle(input_values)

    # Next superheating_ht
    next_superheating_ht, reached_threshold_superheating_ht = calculate_next_x_two_evaporators_cycle(input_values, 
                                                                                                     'superheating_ht',
                                                                                                     y,
                                                                                                     current_cycle, 
                                                                                                     delta, 
                                                                                                     alpha, 
                                                                                                     input_values['lower_threshold'], 
                                                                                                     input_values['upper_threshold'])

    # Next superheating_lt
    next_superheating_lt, reached_threshold_superheating_lt = calculate_next_x_two_evaporators_cycle(input_values, 
                                                                                                     'superheating_lt',
                                                                                                     y,
                                                                                                     current_cycle, 
                                                                                                     delta, 
                                                                                                     alpha, 
                                                                                                     input_values['lower_threshold'], 
                                                                                                     input_values['upper_threshold'])

    # Next subcooling
    next_subcooling, reached_threshold_subcooling = calculate_next_x_two_evaporators_cycle(input_values, 
                                                                                           'subcooling',
                                                                                           y,
                                                                                           current_cycle, 
                                                                                           delta, 
                                                                                           alpha, 
                                                                                           input_values['lower_threshold'], 
                                                                                           input_values['upper_threshold'])
    
    # Next f
    next_f, reached_threshold_f = calculate_next_x_two_evaporators_cycle(input_values, 'f', y, current_cycle, delta, alpha, 0.3, 0.7)
        
    input_values['superheating_ht'] = next_superheating_ht
    input_values['superheating_lt'] = next_superheating_lt
    input_values['subcooling'] = next_subcooling
    input_values['f'] = next_f
    sum_of_threshold_reached =  reached_threshold_superheating_ht + reached_threshold_superheating_lt \
        + reached_threshold_subcooling + reached_threshold_f
    
    next_cycle = calculate_two_evaporators_cycle(input_values)
    
    return sum_of_threshold_reached, current_cycle, next_cycle

def optimize_two_evaporators_cycle(input_values, y):
    n = 0
    error = 1
    while n < 4 and abs(error) >= 10**(-10):
        n, current_cycle, next_cycle = calculate_next_all_two_evaporators_cycle(input_values, y, 10**(-1), 5)
        error = (next_cycle[y] - current_cycle[y])/((next_cycle[y] + current_cycle[y])/2)
    optimized_cycle = calculate_two_evaporators_cycle(input_values)
    return optimized_cycle

def optimize_two_evaporators_cycle_with_multiple_refrigerants(default_input_values, input_values, y ,input_ranges):
    original_input_values = copy.copy(input_values)
    results = pd.DataFrame(columns=['refrigerant',
                                    't_external_env',
                                    'month',
                                    'work',
                                    'monthly_energy_consumption',
                                    'monthly_price',
                                    'q_evaporator_ht',
                                    'q_evaporator_lt',
                                    'subcooling',
                                    'superheating_ht',
                                    'superheating_lt',
                                    'f',
                                    'default_f',
                                    'cop',
                                    'default_cop',
                                    'exergy_efficiency',
                                    'default_exergy_efficiency'])
    n = 0
    for refrigerant in input_ranges['refrigerants']:
        for t_external_env_month in input_ranges['t_external_env_month']:
            n += 1
            default_input_values['refrigerant'] = refrigerant
            default_input_values['t_external_env'] = t_external_env_month[1] + 273.15
            default_cycle = calculate_two_evaporators_cycle(default_input_values)
            input_values = copy.copy(original_input_values)
            input_values['work'] = default_cycle['work']
            input_values['refrigerant'] = refrigerant
            input_values['t_external_env'] = t_external_env_month[1] + 273.15
            optimized_cycle = optimize_two_evaporators_cycle(input_values, y)
            print(str(n * 100 / (len(input_ranges['refrigerants']) * len(input_ranges['t_external_env_month']))) + '%')
            results = results.append({
                'refrigerant': refrigerant,
                't_external_env': t_external_env_month[1],
                'month': t_external_env_month[0],
                'work': optimized_cycle['cycle_inputs']['work'],
                'monthly_energy_consumption': optimized_cycle['cycle_inputs']['work'] * 24 * 30 / 1000,
                'monthly_price': optimized_cycle['cycle_inputs']['work'] * 24 * 30 * 0.694 / 1000,
                'q_evaporator_ht': optimized_cycle['q_evaporator_ht'],
                'q_evaporator_lt': optimized_cycle['q_evaporator_lt'],
                'subcooling': optimized_cycle['cycle_inputs']['subcooling'],
                'superheating_ht': optimized_cycle['cycle_inputs']['superheating_ht'],
                'superheating_lt': optimized_cycle['cycle_inputs']['superheating_lt'],
                'f': optimized_cycle['cycle_inputs']['f'],
                'default_f': default_cycle['f'],
                'cop': optimized_cycle['cop'],
                'default_cop': default_cycle['cop'],
                'exergy_efficiency': optimized_cycle['exergy_efficiency_components'],
                'default_exergy_efficiency': default_cycle['exergy_efficiency_components']
            }, ignore_index=True)
    print('Done')
    return results

def calculate_next_x_basic_cycle(input_values, x, y, current_cycle, delta, alpha, lower_threshold, upper_threshold):
    current_x = input_values[x]
    input_values_x = copy.copy(input_values)
    input_values_x[x] += delta
    gradient_cycle_x = calculate_basic_cycle(input_values_x)
    gradient_x = (gradient_cycle_x[y] - current_cycle[y]) / delta
    next_x = current_x + alpha * gradient_x
    next_x, reached_threshold_x = determine_if_reached_threshold(next_x, lower_threshold, upper_threshold)
    return next_x, reached_threshold_x

def calculate_next_all_basic_cycle(input_values, y, delta, alpha):
      
    current_cycle = calculate_basic_cycle(input_values)

    # Next superheating_ht
    next_superheating, reached_threshold_superheating = calculate_next_x_basic_cycle(input_values, 
                                                                                     'superheating',
                                                                                     y,
                                                                                     current_cycle, 
                                                                                     delta, 
                                                                                     alpha, 
                                                                                     input_values['lower_threshold'], 
                                                                                     input_values['upper_threshold'])

    # Next subcooling
    next_subcooling, reached_threshold_subcooling = calculate_next_x_basic_cycle(input_values, 
                                                                                 'subcooling',
                                                                                 y,
                                                                                 current_cycle, 
                                                                                 delta, 
                                                                                 alpha, 
                                                                                 input_values['lower_threshold'], 
                                                                                 input_values['upper_threshold'])
        
    input_values['superheating'] = next_superheating
    input_values['subcooling'] = next_subcooling
    sum_of_threshold_reached =  reached_threshold_superheating + reached_threshold_subcooling
    
    next_cycle = calculate_basic_cycle(input_values)
    
    return sum_of_threshold_reached, current_cycle, next_cycle

def optimize_basic_cycle(input_values, y):
    n = 0
    error = 1
    while n < 2 and abs(error) >= 10**(-10):
        n, current_cycle, next_cycle = calculate_next_all_basic_cycle(input_values, y, 10**(-1), 5)
        error = (next_cycle[y] - current_cycle[y])/((next_cycle[y] + current_cycle[y])/2)
    optimized_cycle = calculate_basic_cycle(input_values)

    return optimized_cycle

def optimize_basic_cycle_with_multiple_refrigerants(default_input_values, input_values, y, input_ranges):
    original_input_values = copy.copy(input_values)
    results = pd.DataFrame(columns=['refrigerant',
                                    't_external_env',
                                    'month',
                                    'work',
                                    'monthly_energy_consumption',
                                    'monthly_price',
                                    'q_evaporator',
                                    'subcooling',
                                    'superheating',
                                    'cop',
                                    'default_cop',
                                    'exergy_efficiency',
                                    'default_exergy_efficiency'])
    n = 0
    for refrigerant in input_ranges['refrigerants']:
        for t_external_env_month in input_ranges['t_external_env_month']:
            n += 1
            default_input_values['refrigerant'] = refrigerant
            default_input_values['t_external_env'] = t_external_env_month[1] + 273.15
            default_cycle = calculate_basic_cycle(default_input_values)
            input_values = copy.copy(original_input_values)
            input_values['work'] = default_cycle['work']
            input_values['refrigerant'] = refrigerant
            input_values['t_external_env'] = t_external_env_month[1] + 273.15
            optimized_cycle = optimize_basic_cycle(input_values, y)
            print(str(n * 100 / (len(input_ranges['refrigerants']) * len(input_ranges['t_external_env_month']))) + '%')
            results = results.append({
                'refrigerant': refrigerant,
                't_external_env': t_external_env_month[1],
                'month': t_external_env_month[0],
                'work': optimized_cycle['cycle_inputs']['work'],
                'monthly_energy_consumption': optimized_cycle['cycle_inputs']['work'] * 8 * 30 / 1000,
                'monthly_price': optimized_cycle['cycle_inputs']['work'] * 8 * 30 * 0.694 / 1000,
                'q_evaporator': optimized_cycle['q_evaporator'],
                'subcooling': optimized_cycle['cycle_inputs']['subcooling'],
                'superheating': optimized_cycle['cycle_inputs']['superheating'],
                'cop': optimized_cycle['cop'],
                'default_cop': default_cycle['cop'],
                'exergy_efficiency': optimized_cycle['exergy_efficiency_components'],
                'default_exergy_efficiency': default_cycle['exergy_efficiency_components']
            }, ignore_index=True)
    print('Done')
    return results