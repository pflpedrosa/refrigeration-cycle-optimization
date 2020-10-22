from CoolProp.CoolProp import PropsSI as Prop
from Equipamentos import *
import numpy as np

'''# Ciclo com tanque de flash da lista 1 de 2019-1 exercício 5 #
Ciclo5 = Ciclo(9,'R134a')
Ciclo5.Condout(5,P=1200)
Ciclo5.VE(6,450)
Ciclo5.Evapout(1,Pl=200)
Ciclo5.SetMass(8,0.15)
Ciclo5.Compress(2,450,Nis=0.8)
Ciclo5.Tflash(8,7,6)
Ciclo5.Tub(8,9,1,2)
Ciclo5.Tub(3,4,5,6)
Ciclo5.VE(9)
Ciclo5.CalEsp(1)
Ciclo5.Exibir('p','h','m','q')
Q = Ciclo5.q[1]*Ciclo5.m[1]
print(Q)
'''

'''
# Exercicio 3 da lista 2019-2 enviada por email #
Ph = 1400
Pb = 220
Ciclo3_1 = Ciclo(4,'Ammonia')
Ciclo3_1.Evapout(1,Pb,4.6)
Ciclo3_1.CondRef(3,Ph,5.5)
Ciclo3_1.VE(4,Pb)
Ciclo3_1.Compress(2,Ph,Nis=0.78)
Ciclo3_1.CalEsp(1)
Ciclo3_1.TrabC()
Ciclo3_1.COP(1)
print(Ciclo3_1.wc)
Ciclo3_1.Exibir('h','T')
'''

#Exercicio Casco Tubo
Pa = 1200
Pm = 420
Pb = 200
Ciclo5 = Ciclo(9,'R717')
Ciclo5.Evapout(5,Pl=Pb)
Ciclo5.Condout(1,P=Pa)
Ciclo5.VE(2,Pm)
Ciclo5.SetMass(5,0.23)
Ciclo5.Compress(6,Pm,Nis=0.85)
Ciclo5.Tub(1,3,4,5,6,7)
Ciclo5.CondRef(3,Pa,Tsr=6.29)
Ciclo5.Evapout(8,Pl=Pm)
Ciclo5.Compress(9,Pa,Nis=0.85)
Ciclo5.VE(4)
Ciclo5.Estado(7,Pm,273.15+18)
Ciclo5.TCT(3,8)
Ciclo5.Tub(8,9)
Ciclo5.CalEsp(5)
Ciclo5.Exibir('p','h','m','s')
Ciclo5.COP(5)