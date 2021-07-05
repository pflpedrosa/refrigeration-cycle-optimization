# Importando as bibliotecas
from CoolProp.CoolProp import PropsSI, PhaseSI

# Calcula qualquer ponto informando dicionario com duas variaveis
def calculate_point(point):
    variables = ['T', 'H', 'S', 'Q', 'P']
    input_variables = list(point.keys())
    output_variables = [variable for variable in variables if variable not in input_variables]
    output_values = PropsSI(output_variables, 
                            input_variables[0], 
                            point[input_variables[0]], 
                            input_variables[1], 
                            point[input_variables[1]], 
                            point['refrigerant']
    )

    for index, variable in enumerate(output_variables):
        point[variable] = output_values[index]

    return point

# Calcula ciclo basico baseado nas variaveis de entrada (trabalho)
def calculate_basic_cycle_with_work(cycle_inputs):
    t_0 = cycle_inputs['t_external_env']
    
    point_1_saturado = {'Q': 1, 
                        'T': cycle_inputs['t_internal_env'] - cycle_inputs['approach_evaporator'],
                        'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_1_saturado)

    if cycle_inputs['superheating'] > 0:
        point_1 = {'P': point_1_saturado['P'], 
                'T': point_1_saturado['T'] + cycle_inputs['superheating'],
                'refrigerant': cycle_inputs['refrigerant']
                }
        calculate_point(point_1)
    else:
        point_1 = point_1_saturado

    point_3_saturado = {'Q': 0, 
                        'T': cycle_inputs['t_external_env'] + cycle_inputs['approach_condenser'],
                       'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_3_saturado)

    if cycle_inputs['subcooling'] > 0:
        point_3 = {'P': point_3_saturado['P'], 
                'T': point_3_saturado['T'] - cycle_inputs['subcooling'],
                'refrigerant': cycle_inputs['refrigerant']
                }
        calculate_point(point_3)
    else:
        point_3 = point_3_saturado

    point_2_isen = {'S': point_1['S'], 
                    'P': point_3['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                   }
    calculate_point(point_2_isen)

    point_2 = {'P': point_3['P'], 
               'H': point_1['H'] + (point_2_isen['H'] - point_1['H']) / cycle_inputs['isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_2)

    point_4 = {'P': point_1['P'], 
               'H': point_3['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_4)

    m = cycle_inputs['work'] / (point_2['H'] - point_1['H']) 
    q_evaporator = m * (point_1['H'] - point_4['H'])
    cop = q_evaporator / cycle_inputs['work'] 
    cop_carnot = cycle_inputs['t_internal_env'] / (cycle_inputs['t_external_env'] - cycle_inputs['t_internal_env'])

    compressor_exergy_destruction = m * t_0 * (point_2['S'] - point_1['S'])
    condenser_exergy_destruction = m * t_0 * (point_3['S'] - point_2['S'] + (point_2['H'] - point_3['H']) / cycle_inputs['t_external_env'])
    expansion_valve_exergy_destruction = m * t_0 * (point_4['S'] - point_3['S'])
    evaporator_exergy_destruction = m * t_0 * (point_1['S'] - point_4['S'] - (point_1['H'] - point_4['H']) / cycle_inputs['t_internal_env'])
    total_exergy_destruction = compressor_exergy_destruction + condenser_exergy_destruction + expansion_valve_exergy_destruction + evaporator_exergy_destruction
    
    return {
        'cycle_inputs': cycle_inputs,
        'point_1': point_1,
        'point_2': point_2,
        'point_3': point_3,
        'point_4': point_4,
        'm': m,
        'q_evaporator': q_evaporator,
        'cop': cop,
        'exergy_efficiency': cop / cop_carnot,
        'exergy_efficiency_components': 1 - total_exergy_destruction / (m * (point_2['H'] - point_1['H']))
    }

# Calcula ciclo basico baseado nas variaveis de entrada (potencia frigorifica)
def calculate_basic_cycle_with_q_evaporator(cycle_inputs):
    t_0 = cycle_inputs['t_external_env']
    
    point_1_saturado = {'Q': 1, 
                        'T': cycle_inputs['t_internal_env'] - cycle_inputs['approach_evaporator'],
                        'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_1_saturado)

    if cycle_inputs['superheating'] > 0:
        point_1 = {'P': point_1_saturado['P'], 
                'T': point_1_saturado['T'] + cycle_inputs['superheating'],
                'refrigerant': cycle_inputs['refrigerant']
                }
        calculate_point(point_1)
    else:
        point_1 = point_1_saturado

    point_3_saturado = {'Q': 0, 
                        'T': cycle_inputs['t_external_env'] + cycle_inputs['approach_condenser'],
                       'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_3_saturado)

    if cycle_inputs['subcooling'] > 0:
        point_3 = {'P': point_3_saturado['P'], 
                'T': point_3_saturado['T'] - cycle_inputs['subcooling'],
                'refrigerant': cycle_inputs['refrigerant']
                }
        calculate_point(point_3)
    else:
        point_3 = point_3_saturado

    point_2_isen = {'S': point_1['S'], 
                    'P': point_3['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                   }
    calculate_point(point_2_isen)

    point_2 = {'P': point_3['P'], 
               'H': point_1['H'] + (point_2_isen['H'] - point_1['H']) / cycle_inputs['isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_2)

    point_4 = {'P': point_1['P'], 
               'H': point_3['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_4)

    m = cycle_inputs['q_evaporator'] / (point_1['H'] - point_4['H'])
    work = m * (point_2['H'] - point_1['H'])
    cop = cycle_inputs['q_evaporator'] / work 
    cop_carnot = cycle_inputs['t_internal_env'] / (cycle_inputs['t_external_env'] - cycle_inputs['t_internal_env'])
    
    compressor_exergy_destruction = m * t_0 * (point_2['S'] - point_1['S'])
    condenser_exergy_destruction = m * t_0 * (point_3['S'] - point_2['S'] + (point_2['H'] - point_3['H']) / cycle_inputs['t_external_env'])
    expansion_valve_exergy_destruction = m * t_0 * (point_4['S'] - point_3['S'])
    evaporator_exergy_destruction = m * t_0 * (point_1['S'] - point_4['S'] - (point_1['H'] - point_4['H']) / cycle_inputs['t_internal_env'])
    total_exergy_destruction = compressor_exergy_destruction + condenser_exergy_destruction + expansion_valve_exergy_destruction + evaporator_exergy_destruction
    
    return {
        'cycle_inputs': cycle_inputs,
        'point_1': point_1,
        'point_2': point_2,
        'point_3': point_3,
        'point_4': point_4,
        'm': m,
        'work': work,
        'cop': cop,
        'exergy_efficiency': cop / cop_carnot,
        'exergy_efficiency_components': 1 - total_exergy_destruction / (m * (point_2['H'] - point_1['H']))
    }

# Calcula ciclo de dois evaporadores baseado nas variaveis de entrada (trabalho e f)
def calculate_two_evaporators_cycle_with_work_and_f(cycle_inputs):

    # Point 3 (after condenser)
    point_3_saturado = {'Q': 0, 
                        'T': cycle_inputs['t_external_env'] + cycle_inputs['approach_condenser'],
                       'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_3_saturado)

    if cycle_inputs['subcooling'] > 0:
        point_3 = {'P': point_3_saturado['P'], 
                   'T': point_3_saturado['T'] - cycle_inputs['subcooling'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        calculate_point(point_3)
    else:
        point_3 = point_3_saturado
        
    # Point 5 (after high temperature evaporator)    
    point_5_saturado = {'Q': 1, 
                        'T': cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht'],
                        'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_5_saturado)
    
    if cycle_inputs['superheating_ht'] > 0:
        point_5 = {'P': point_5_saturado['P'], 
                   'T': point_5_saturado['T'] + cycle_inputs['superheating_ht'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        calculate_point(point_5)
    else:
        point_5 = point_5_saturado

    # Point 8 (after low temperature evaporator)  
    point_8_saturado = {'Q': 1, 
                        'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
                        'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_8_saturado)

    if cycle_inputs['superheating_lt'] > 0:
        point_8 = {'P': point_8_saturado['P'], 
                   'T': point_8_saturado['T'] + cycle_inputs['superheating_lt'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        calculate_point(point_8)    
    else:
        point_8 = point_8_saturado
    
    # Point 4 (after expansion valve of HTE)  
    point_4 = {'P': point_5['P'], 
               'H': point_3['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_4)

    # Point 7 (after expansion valve of LTE)  
    point_7 = {'P': point_8['P'], 
               'H': point_3['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_7)
    
    # Point 6 (after regulator expansion valve)  
    point_6 = {'P': point_8['P'], 
               'H': point_5['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_6)
    
    # Point 1 (before compressor)
    point_1 = {'P': point_8['P'],
               'H': (1 - cycle_inputs['f']) * point_6['H'] + cycle_inputs['f'] * point_8['H'],
               'refrigerant': cycle_inputs['refrigerant']
    }
    calculate_point(point_1)
    
    # Point 2 (after compressor)
    point_2_isen = {'S': point_1['S'], 
                    'P': point_3['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                   }
    calculate_point(point_2_isen)

    point_2 = {'P': point_3['P'], 
               'H': point_1['H'] + (point_2_isen['H'] - point_1['H']) / cycle_inputs['isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_2)
    
    # Masses
    m = cycle_inputs['work'] / (point_2['H'] - point_1['H'])
    m_lt = m * cycle_inputs['f']
    m_ht = m * (1 - cycle_inputs['f'])
    
    # COP
    q_evaporator_ht = m_ht * (point_5['H'] - point_4['H'])
    q_evaporator_lt = m_lt * (point_8['H'] - point_7['H'])
    cop = (q_evaporator_ht + q_evaporator_lt) / cycle_inputs['work'] 
    
    # Exergy Destruction
    cop_carnot_ht = cycle_inputs['t_internal_env_ht'] / (cycle_inputs['t_external_env'] - cycle_inputs['t_internal_env_ht'])
    cop_carnot_lt = cycle_inputs['t_internal_env_lt'] / (cycle_inputs['t_external_env'] - cycle_inputs['t_internal_env_lt'])
    
    w_carnot_ht = q_evaporator_ht / cop_carnot_ht
    w_carnot_lt = q_evaporator_lt / cop_carnot_lt
    
    cop_carnot = (q_evaporator_ht + q_evaporator_lt) / (w_carnot_ht + w_carnot_lt)
    
    # Exergy Destruction Components
    t_0 = cycle_inputs['t_external_env']
    
    compressor_exergy_destruction = m * t_0 * (point_2['S'] - point_1['S'])
    condenser_exergy_destruction = m * t_0 * (point_3['S'] - point_2['S'] + (point_2['H'] - point_3['H']) / cycle_inputs['t_external_env'])
    expansion_valve_ht_exergy_destruction = m_ht * t_0 * (point_4['S'] - point_3['S'])
    evaporator_ht_exergy_destruction = m_ht * t_0 * (point_5['S'] - point_4['S'] - (point_5['H'] - point_4['H']) / cycle_inputs['t_internal_env_ht'])
    regulator_expansion_valve_exergy_destruction = m_ht * t_0 * (point_6['S'] - point_5['S'])
    expansion_valve_lt_exergy_destruction = m_lt * t_0 * (point_7['S'] - point_3['S'])
    evaporator_lt_exergy_destruction = m_lt * t_0 * (point_8['S'] - point_7['S'] - (point_8['H'] - point_7['H']) / cycle_inputs['t_internal_env_lt'])
    
    total_exergy_destruction = compressor_exergy_destruction + condenser_exergy_destruction + expansion_valve_ht_exergy_destruction + \
        evaporator_ht_exergy_destruction + regulator_expansion_valve_exergy_destruction + \
        expansion_valve_lt_exergy_destruction + evaporator_lt_exergy_destruction
    
    return {
        'cycle_inputs': cycle_inputs,
        'point_1': point_1,
        'point_2': point_2,
        'point_3': point_3,
        'point_4': point_4,
        'point_5': point_5,
        'point_6': point_6,
        'point_7': point_7,
        'point_8': point_8,
        'm': m,
        'm_ht': m_ht,
        'm_lt': m_lt,
        'q_evaporator_ht': q_evaporator_ht,
        'q_evaporator_lt': q_evaporator_lt,
        'cop': cop,
        'exergy_efficiency': cop / cop_carnot,
        'exergy_efficiency_components': 1 - total_exergy_destruction / cycle_inputs['work']
    }

# Calcula ciclo de dois evaporadores baseado nas variaveis de entrada (potencias frigorificas)
def calculate_two_evaporators_cycle_with_q_evaporators(cycle_inputs):

    # Point 3 (after condenser)
    point_3_saturado = {'Q': 0, 
                        'T': cycle_inputs['t_external_env'] + cycle_inputs['approach_condenser'],
                       'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_3_saturado)

    if cycle_inputs['subcooling'] > 0:
        point_3 = {'P': point_3_saturado['P'], 
                   'T': point_3_saturado['T'] - cycle_inputs['subcooling'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        calculate_point(point_3)
    else:
        point_3 = point_3_saturado
        
    # Point 5 (after high temperature evaporator)    
    point_5_saturado = {'Q': 1, 
                        'T': cycle_inputs['t_internal_env_ht'] - cycle_inputs['approach_evaporator_ht'],
                        'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_5_saturado)
    
    if cycle_inputs['superheating_ht'] > 0:
        point_5 = {'P': point_5_saturado['P'], 
                   'T': point_5_saturado['T'] + cycle_inputs['superheating_ht'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        calculate_point(point_5)
    else:
        point_5 = point_5_saturado

    # Point 8 (after low temperature evaporator)  
    point_8_saturado = {'Q': 1, 
                        'T': cycle_inputs['t_internal_env_lt'] - cycle_inputs['approach_evaporator_lt'],
                        'refrigerant': cycle_inputs['refrigerant']
                       }
    calculate_point(point_8_saturado)

    if cycle_inputs['superheating_lt'] > 0:
        point_8 = {'P': point_8_saturado['P'], 
                   'T': point_8_saturado['T'] + cycle_inputs['superheating_lt'],
                   'refrigerant': cycle_inputs['refrigerant']
                  }
        calculate_point(point_8)    
    else:
        point_8 = point_8_saturado      
    
    # Point 4 (after expansion valve of HTE)  
    point_4 = {'P': point_5['P'], 
               'H': point_3['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_4)

    # Point 7 (after expansion valve of LTE)  
    point_7 = {'P': point_8['P'], 
               'H': point_3['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_7)
    
    # Point 6 (after regulator expansion valve)  
    point_6 = {'P': point_8['P'], 
               'H': point_5['H'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_6)
    
    # Masses
    m_ht = cycle_inputs['q_evaporator_ht'] / (point_5['H'] - point_4['H'])
    m_lt = cycle_inputs['q_evaporator_lt'] / (point_8['H'] - point_7['H'])
    m = m_ht + m_lt
    f = m_lt / m

    # Point 1 (before compressor)
    point_1 = {'P': point_8['P'],
               'H': (1 - f) * point_6['H'] + f * point_8['H'],
               'refrigerant': cycle_inputs['refrigerant']
    }
    calculate_point(point_1)
    
    # Point 2 (after compressor)
    point_2_isen = {'S': point_1['S'], 
                    'P': point_3['P'],
                    'refrigerant': cycle_inputs['refrigerant']
                   }
    calculate_point(point_2_isen)

    point_2 = {'P': point_3['P'], 
               'H': point_1['H'] + (point_2_isen['H'] - point_1['H']) / cycle_inputs['isentropic_efficiency'],
               'refrigerant': cycle_inputs['refrigerant']
              }
    calculate_point(point_2)
    
    # Work
    work = m * (point_2['H'] - point_1['H'])
    
    # COP
    cop = (cycle_inputs['q_evaporator_ht'] + cycle_inputs['q_evaporator_lt']) / work
    
    # Exergy Destruction
    cop_carnot_ht = cycle_inputs['t_internal_env_ht'] / (cycle_inputs['t_external_env'] - cycle_inputs['t_internal_env_ht'])
    cop_carnot_lt = cycle_inputs['t_internal_env_lt'] / (cycle_inputs['t_external_env'] - cycle_inputs['t_internal_env_lt'])
    
    w_carnot_ht = cycle_inputs['q_evaporator_ht'] / cop_carnot_ht
    w_carnot_lt = cycle_inputs['q_evaporator_lt'] / cop_carnot_lt
    
    cop_carnot = (cycle_inputs['q_evaporator_ht'] + cycle_inputs['q_evaporator_lt']) / (w_carnot_ht + w_carnot_lt)
    
    # Exergy Destruction Components
    t_0 = cycle_inputs['t_external_env']
    
    compressor_exergy_destruction = m * t_0 * (point_2['S'] - point_1['S'])
    condenser_exergy_destruction = m * t_0 * (point_3['S'] - point_2['S'] + (point_2['H'] - point_3['H']) / cycle_inputs['t_external_env'])
    expansion_valve_ht_exergy_destruction = m_ht * t_0 * (point_4['S'] - point_3['S'])
    evaporator_ht_exergy_destruction = m_ht * t_0 * (point_5['S'] - point_4['S'] - (point_5['H'] - point_4['H']) / cycle_inputs['t_internal_env_ht'])
    regulator_expansion_valve_exergy_destruction = m_ht * t_0 * (point_6['S'] - point_5['S'])
    expansion_valve_lt_exergy_destruction = m_lt * t_0 * (point_7['S'] - point_3['S'])
    evaporator_lt_exergy_destruction = m_lt * t_0 * (point_8['S'] - point_7['S'] - (point_8['H'] - point_7['H']) / cycle_inputs['t_internal_env_lt'])
    
    total_exergy_destruction = compressor_exergy_destruction + condenser_exergy_destruction + expansion_valve_ht_exergy_destruction + \
        evaporator_ht_exergy_destruction + regulator_expansion_valve_exergy_destruction + \
        expansion_valve_lt_exergy_destruction + evaporator_lt_exergy_destruction
    
    return {
        'cycle_inputs': cycle_inputs,
        'point_1': point_1,
        'point_2': point_2,
        'point_3': point_3,
        'point_4': point_4,
        'point_5': point_5,
        'point_6': point_6,
        'point_7': point_7,
        'point_8': point_8,
        'm': m,
        'm_ht': m_ht,
        'm_lt': m_lt,
        'f': f,
        'work': work,
        'cop': cop,
        'exergy_efficiency': cop / cop_carnot,
        'exergy_efficiency_components': 1 - total_exergy_destruction / work
    }