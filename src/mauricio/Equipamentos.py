# -*- coding: cp1252 -*-
# 
## ESTADOS TERMODINAMICOS DO FLUIDO ##
from CoolProp.CoolProp import PropsSI as Prop
from sympy import symbols, Eq, solve
class Ciclo:
    def __init__(self,n,fluid):
        self.fluid=fluid
        self.n = n
        self.p=['Pressao (kPa):']+["-"]*n
        self.h=['Entalpia (kJ/kg):']+["-"]*n
        self.s=['Entropia (kJ/kgK):']+["-"]*n
        self.T=['Temperatura (K):']+["-"]*n
        self.x=['Titulo:']+["-"]*n
        self.y=['Fracao massica']+["-"]*n
        self.m=['Vazão mássica']+["-"]*n
        self.sang = -1
        self.yc=[]
        self.equip={}
        self.wt={}
        self.wb={}
        self.q={}
        self.wc={}
        self.n={}

    def caldout(self,i,j=0,P='sat',T='sat'):
        k = 0
        self.equip[i] = 'Caldeira'
        if P == 'sat':
            k += 1
            P = Prop('P','T',T,'Q',1,self.fluid)/1e3
            if i == 1:
                if j == 0:
                    self.p[i] = self.p[i-2] = P
                    self.y[i] = self.y[i-2] = 1
                else:
                    self.p[i] = self.p[j] = P
                    self.y[i] = self.y[j] = 1
            else:
                if j == 0:
                    self.p[i] = self.p[i-1] = P
                    self.y[i] = self.y[i-1] = 1
                else:
                    self.p[i] = self.p[i-1] = P
                    self.y[i] = self.y[i-1] = 1
        else:
            if i == 1:
                if j == 0:
                    self.p[i] = self.p[i-2] = P
                    self.y[i] = self.y[i-2] = 1
                else:
                    self.p[i] = self.p[j] = P
                    self.y[i] = self.y[j] = 1
            else:
                if j == 0:
                    self.p[i] = self.p[i-1] = P
                    self.y[i] = self.y[i-1] = 1
                else:
                    self.p[i] = self.p[j] = P
                    self.y[i] = self.y[j] = 1
        if T == 'sat':
            k +=1
            T = Prop('T','P',P*1e3,'Q',1,self.fluid)
            self.T[i] = T
        else:
            self.T[i] = T
        if k == 0:
            self.h[i] = Prop('H','P',P*1e3,'T',T,self.fluid)/1e3
            self.s[i] = Prop('S','P',P*1e3,'T',T,self.fluid)/1e3
        else:
            self.h[i] = Prop('H','P',P*1e3,'Q',1,self.fluid)/1e3
            self.s[i] = Prop('S','P',P*1e3,'Q',1,self.fluid)/1e3

    def turbina(self,i,j,P,T=0,n=1):
        self.equip[i] = 'Turbina'
        if T == 0:
            if self.h[i] == '-':
                self.sang += 1
            else:
                self.sang = self.sang
            self.p[i] = P
            self.s[i] = self.s[j]
            self.x[i] = Prop('Q','P',P*1e3,'S',self.s[i]*1e3,self.fluid)
            self.h[i] = Prop('H','P',P*1e3,'S',self.s[i]*1e3,self.fluid)/1e3
            self.T[i] = Prop('T','P',P*1e3,'S',self.s[i]*1e3,self.fluid)
            wi = self.h[j] - self.h[i]
            wt = round(wi*n,2)
            self.n[i] = n
            self.wt[i] = wt
        else:
            self.T[i] = T
            if self.h[i] == '-':
                self.sang += 1
            else:
                self.sang = self.sang
            self.p[i] = P
            self.x[i] = Prop('Q','P',P*1e3,'T',T,self.fluid)
            self.h[i] = Prop('H','P',P*1e3,'T',T,self.fluid)/1e3
            self.s[i] = Prop('S','P',P*1e3,'T',T,self.fluid)/1e3
            wt = self.h[j] - self.h[i]
            self.wt[i] = wt
            si = self.s[j]
            hi = Prop('H','P',P*1e3,'S',si*1e3,self.fluid)/1e3
            wi = self.h[j] - hi
            n = wt/wi
            self.n[i] = n
        return wt

    def Condout(self,i,j=0,P='sat',T='sat'):
        k = 0
        self.equip[i] = 'Condensador'
        if P == 'sat':
            k += 1
            P = Prop('P','T',T,'Q',0,self.fluid)/1e3
            if j == 0:
                if i == 1:
                    self.p[i] = self.p[i-2] = P
                else:
                    self.p[i] = self.p[i-1] = P
            else:
                self.p[i] = self.p[j] = P
        else:
            if j == 0:
                if i == 1:
                    self.p[i] = self.p[i-2] = P
                else:
                    self.p[i] = self.p[i-1] = P
            else:
                self.p[i] = self.p[j] = P
        if T == 'sat':
            k += 1
            T = Prop('T','P',P*1e3,'Q',0,self.fluid)
            if j ==0:
                if i == 1:
                    self.p[i-2] = self.p[i] = P
                else:
                    self.p[i-1] = self.p[i] = P
            else:
                self.p[j] = self.p[i]            
        if k != 0:
            self.h[i] = Prop('H','P',P*1e3,'Q',0,self.fluid)/1e3
            self.s[i] = Prop('S','P',P*1e3,'Q',0,self.fluid)/1e3
            self.T[i] = Prop('T','P',P*1e3,'Q',0,self.fluid)
        else:
            self.h[i] = Prop('H','P',P*1e3,'T',T,self.fluid)/1e3
            self.s[i] = Prop('S','P',P*1e3,'T',T,self.fluid)/1e3
            self.T[i] = T

    def Bomba(self,i,Pm = 0,Pj = 0,Tm=0):
        self.equip[i] = 'Bomba'
        if Pm == 0:
            Pm = self.p[i]
        else:
            self.p[i] = Pm
        if Pj == 0:
            if i == 1:
                Pj = self.p[i-2]
            else:
                Pj = self.p[i-1]
        if Tm == 0:
            vj = Prop('D','P',Pj*1e3,'Q',0,self.fluid)**-1
            vm = Prop('D','P',Pm*1e3,'Q',0,self.fluid)**-1
            v = (vj+vm)/2
            wb = round(v*(Pm-Pj),2)
            self.wb[i] = wb
            if i == 1:
                self.h[i-2] = Prop('H','P',Pj*1e3,'Q',0,self.fluid)/1e3
                self.h[i] = self.h[i-2] + wb
                self.y[i] = self.y[i-2]
            else:
                self.h[i-1] = Prop('H','P',Pj*1e3,'Q',0,self.fluid)/1e3
                self.h[i] = self.h[i-1] + wb
                self.y[i] = self.y[i-1]
        else:
            self.h[i] = Prop('H','P',Pm*1e3,'T',Tm,self.fluid)/1e3
            self.T[i] = Tm
            if i == 1:
                wb = self.h[i]-self.h[i-2]
            else:
                wb = self.h[i]-self.h[i-1]
            self.wb[i] = wb
        return wb

    def CalEsp(self,i,j=0):
        if j == 0:
            if i == 1:
                self.q[i] = self.h[i] - self.h[i-2]
            else:
                self.q[i] = self.h[i] - self.h[i-1]
        else:
            self.q[i] = self.h[i] - self.h[j]
        return self.q[i]

    def TrabB(self):
        self.Wb = 0
        for i in self.wb:
            if self.y[i] == '-':
                if i == 1:
                    self.y[i] = self.y[i-2]
                else:
                    self.y[i] = self.y[i-1]
            self.Wb += self.wb[i]*self.y[i]
        return self.Wb

    def TrabT(self):
        self.Wt = 0
        sf = 0
        for i in self.wt:
            if self.y[i] != '-':
                sf += self.y[i]
        for i in self.wt:
            if self.y[i] == '-':
                self.y[i] = 1 - sf
            self.Wt += self.wt[i]*self.y[i]
        return self.Wt

    def TrabC(self):
        self.Wc = 0
        for i in self.wc:
            if self.y[i] != '-':
                self.Wc += self.wc[i]*self.y[i]
                print('Trabalho calculado usando fracao massica')
            elif self.m[i] != '-':
                self.Wc += self.wc[i]*self.m[i]
                print('Trabalho calculado usando vazao massica')
            else:
                self.Wc += self.wc[i]
                print('Trabalho calculado supondo fluxo unico no ciclo')
        return self.Wc
    
    def rend(self):
        Q=0
        for i in self.q:
            Q += self.q[i]
        self.rend = (self.TrabT() - self.TrabB() - self.TrabC())/Q
        return self.rend

    def AC(self,i,j,k):
        fluxo = 0
        self.p[i] = self.p[k] = self.p[j]
        self.h[i] = Prop('H','P',self.p[i]*1e3,'Q',0,self.fluid)/1e3
        if len(self.yc) == 0:
            self.y[j] = (self.h[i]-self.h[k])/(self.h[j]-self.h[k])
            self.y[i] = 1
            self.y[k] = 1 - self.y[j]
            self.yc.append(self.y[j])
        else:
            for i in range(len(yc)):
                fluxo += self.yc[i]
            self.y[j] = (1 - fluxo)*(self.h[i]-self.h[k])/(self.h[j]-self.h[k])
            self.y[i] = fluxo
            self.y[k] = self.y[i] - self.y[j]
            self.yc.append(y[j])

    def VE(self,i,P=None,j=0):
        if P != None:
            self.p[i] = P
        if j == 0:
            if i == 1:
                j = i - 2
            else:
                j = i - 1
        self.h[i] = self.h[j]
        self.y[i] = self.y[j]
        self.s[i] = Prop('S','H',self.h[i]*1e3,'P',self.p[i]*1e3,self.fluid)/1e3

    def ASi(self,m,ti,to,r=0):
        # igualando pressao do duto para caldeira
        if m == 1:
            if self.p[m] == '-':
                self.p[m] = self.p[m-2]
            else:
                self.p[m-2] = self.p[m]
        else:
            if self.p[m] == '-':
                self.p[m] = self.p[m-1]
            else:
                self.p[m-1] = self.p[m]
        # Supondo estado saturação na saida do trocador (após turbina)
        self.p[to] = self.p[ti]
        self.h[to] = Prop('H','P',self.p[to]*1e3,'Q',0,self.fluid)/1e3
        self.T[to] = Prop('T','P',self.p[to]*1e3,'Q',0,self.fluid)
        # Supondo as temperaturas de saida iguais
        self.T[m] = self.T[to]
        self.h[m] = Prop('H','P',self.p[m]*1e3,'T',self.T[m],self.fluid)/1e3

    def ASTI(self,m,ti,to,r=0,j=0):
        # igualando pressao do duto para caldeira
        if j == 0:
            if m == 1:
                if self.p[m] == '-':
                    self.p[m-2] = self.p[m]
                else:
                    self.p[m] = self.p[m-2]
            else:
                if self.p[m] == '-':
                    self.p[m] = self.p[m-1]
                else:
                    self.p[m-1] = self.p[m]
        else:
            if self.p[m] == '-':
                self.p[m] = self.p[j]
            else:
                self.p[j] = self.p[m]
        # Supondo estado saturação na saida do trocador (após turbina)
        self.p[to] = self.p[ti]
        self.h[to] = Prop('H','P',self.p[to]*1e3,'Q',0,self.fluid)/1e3
        self.T[to] = Prop('T','P',self.p[to]*1e3,'Q',0,self.fluid)
        # Supondo as temperaturas de saida iguais
        self.T[m] = self.T[to]
        self.h[m] = Prop('H','P',self.p[m]*1e3,'T',self.T[m],self.fluid)/1e3
        # Realizando o balanço de energia
        if r == 0:
            if m == 1:
                self.y[ti] = self.y[to] = (self.h[m] - self.h[m-2])/(self.h[ti]-self.h[to])
            else:
                self.y[ti] = self.y[to] = (self.h[m] - self.h[m-1])/(self.h[ti]-self.h[to])
        else:
            if m == 1:
                self.y[ti] = ((self.h[to]-self.h[r])*self.y[r] + self.h[m] - self.h[m-2])/(self.h[ti]-self.h[to])
            else:
                self.y[ti] = ((self.h[to]-self.h[r])*self.y[r] + self.h[m] - self.h[m-1])/(self.h[ti]-self.h[to])

    def Evapout(self,i,Pl='sat',Tsa ='sat'):
        if Pl == 'sat':
            self.p[i] = Prop('P','T',T,'Q',1,self.fluid)/1e3
            Pl = self.p[i]
            self.h[i] = Prop('H','P',Pl*1e3,'Q',1,self.fluid)/1e3
            self.s[i] = Prop('S','P',Pl*1e3,'Q',1,self.fluid)/1e3
        else:        
            if Tsa == 'sat':
                self.T[i] = Prop('T','P',Pl*1e3,'Q',1,self.fluid)
                self.h[i] = Prop('H','P',Pl*1e3,'Q',1,self.fluid)/1e3
                self.s[i] = Prop('S','P',Pl*1e3,'Q',1,self.fluid)/1e3
            else:
                self.T[i] = Prop('T','P',Pl*1e3,'Q',1,self.fluid) + Tsa
                self.h[i] = Prop('H','P',Pl*1e3,'T',self.T[i],self.fluid)/1e3
                self.s[i] = Prop('S','P',Pl*1e3,'T',self.T[i],self.fluid)/1e3
        if i == 1:
            self.p[i] = self.p[i-2] = Pl
            if self.h[i-2] != '-':
                self.q[i] = self.h[i] - self.h[i-2]
        else:
            self.p[i-1] = self.p[i] = Pl
            if self.h[i-1] != '-':
                self.q[i] = self.h[i]-self.h[i-1]

    def CondRef(self,i,Ph,Tsr='sat'):
        self.p[i] = Ph
        if Tsr == 'sat':
            self.T[i] = Prop('T','P',Ph*1e3,'Q',0,self.fluid)
            self.h[i] = round(Prop('H','P',Ph*1e3,'Q',0,self.fluid)/1e3,2)
            self.s[i] = round(Prop('S','P',Ph*1e3,'Q',0,self.fluid)/1e3,2)
        else:
            self.T[i] = Prop('T','P',Ph*1e3,'Q',0,self.fluid) - Tsr
            self.h[i] = round(Prop('H','P',Ph*1e3,'T',self.T[i],self.fluid)/1e3,2)
            self.s[i] = round(Prop('S','P',Ph*1e3,'T',self.T[i],self.fluid)/1e3,2)
        if i == 1:
            self.p[i-2] = Ph
            if self.h[i-2] != '-':
                self.q[i] = self.h[i] - self.h[i-2]
        else:
            self.p[i-1] = Ph
            if self.h[i-1] != '-':
                self.q[i] = self.h[i]-self.h[i-1]

    def Compress(self,i,P,j=0,Nis=1):
            self.p[i] = P
            if self.h[i] == '-':
                self.n[i] = Nis
                if j == 0:
                    if i == 1:
                        self.s[i] = self.s[i-2]
                        self.h[i] = Prop('H','S',self.s[i]*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        wci = self.h[i] - self.h[i-2]
                        self.wc[i] = wci/Nis
                        self.h[i] = self.h[i-2] + self.wc[i]
                        self.s[i] = Prop('S','H',self.h[i]*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        self.T[i] = Prop('T','H',self.h[i]*1e3,'P',self.p[i]*1e3,self.fluid)
                    else:
                        self.s[i] = self.s[i-1]
                        self.h[i] = Prop('H','S',self.s[i]*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        wci = self.h[i] - self.h[i-1]
                        self.wc[i] = wci/Nis
                        self.h[i] = self.h[i-1] + self.wc[i]
                        self.s[i] = Prop('S','H',self.h[i]*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        self.T[i] = Prop('T','H',self.h[i]*1e3,'P',self.p[i]*1e3,self.fluid)
                else:
                        self.s[i] = self.s[j]
                        self.h[i] = Prop('H','S',self.s[i]*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        self.wc[i] = (self.h[i] - self.h[j])/Nis
                        self.h[i] = self.h[j] + self.wc[i]
                        self.s[i] = Prop('S','H',self.h[i]*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        self.T[i] = Prop('T','H',self.h[i]*1e3,'P',self.p[i]*1e3,self.fluid)
            else:
                if j == 0:
                    if i == 1:
                        si = self.s[i-2]
                        hi = Prop('H','S',si*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        wci = hi - self.h[i-2]
                        self.wc[i] = self.h[i] - self.h[i-2]
                        self.n[i] = wci/self.wc[i]
                    else:
                        si = self.s[i-1]
                        hi = Prop('H','S',si*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        wci = hi - self.h[i-1]
                        self.wc[i] = self.h[i] - self.h[i-1]
                        self.n[i] = wci/self.wc[i]
                else:
                        si = self.s[j]
                        hi = Prop('H','S',si*1e3,'P',self.p[i]*1e3,self.fluid)/1e3
                        wci = hi - self.h[j]
                        self.wc[i] = self.h[i] - self.h[j]
                        self.n[i] = wci/self.wc[i]

    def Estado(self,i,P,T):
        self.T[i] = T
        self.p[i] = P
        self.h[i] = Prop('H','P',P*1e3,'T',T,self.fluid)/1e3
        self.s[i] = Prop('S','P',P*1e3,'T',T,self.fluid)/1e3

    def EnergyB(self,s1,s2,e1,e2):
        if self.y[s1] == '-':   
            self.y[s1] = self.y[e1] = (self.y[s2]*(self.h[s2]-self.h[e2]))/(self.h[e1]-self.h[s1])
            if self.y[s1] > 1 or self.y[s1] < 0:
                raise ValueError
        else:
            self.y[s2] = self.y[e2] = (self.y[s1]*(self.h[s1]-self.h[e1]))/(self.h[e2]-self.h[s2])
            if self.y[s2] > 1 or self.y[s2] < 0:
                raise ValueError

    def fluxsep(self,*kargs):
        k = 0
        sf = 0
        for i in kargs:
            if self.y[i] != '-':
                sf += self.y[i]
                k += 1
        if k != len(kargs)-1:
            print('Vazoes insuficientes para calculo')
        for i in kargs:
            if self.y[i] == '-':
                self.y[i] = 1 - sf

    def Tflash(self,l,v,*args,P=0):
        # CASO O PARAMETRO P NAO SEJA PASSADO, HAVERA UMA VERIFICAÇÃO
        # PARA IDENTIFICAR SE ALGUM DOS PONTOS POSSUI UMA PRESSÃO DEFINIDA
        # IGUALANDO-A PARA TODOS OS PONTOS DO TFLASH
        if P == 0:
            if self.p[l] != '-':
                ptf = self.p[l]
                for i in args:
                    self.p[i] = ptf
                self.p[v] = ptf
                P = ptf
            if self.p[v] != '-':
                ptf = self.p[v]
                for i in args:
                    self.p[i] = ptf
                self.p[l] = ptf
                P = ptf
            else:
                for k in args:
                    if self.p[k] != '-':
                        ptf = self.p[k]
                for i in args:
                    self.p[i] = ptf
                self.p[v] = ptf
                self.p[l] = ptf
                P = ptf
        else:
            for k in args:
                self.p[k] = P
            self.p[l] = P
            self.p[v] = P
        # CALCULANDO OS ESTADOS DE SAIDA SATURADOS
        self.h[l]=Prop('H','P',P*1e3,'Q',0,self.fluid)/1e3
        self.h[v]=Prop('H','P',P*1e3,'Q',1,self.fluid)/1e3
        ## ANALISANDO QTDE DE VARIAVEIS ##
        if len(args) == 1:
            for i in args:
                self.y[l] = (self.h[i] - self.h[v])/(self.h[l]-self.h[v])
                self.y[v] = 1 - self.y[l]
                self.y[i] = 1
                if self.m[l] != '-':
                    self.m[i] = self.m[l]/self.y[l]
                    self.m[v] = self.m[i] - self.m[l]
                elif self.m[i] != '-':
                    self.m[l] = self.y[l]*self.m[i]
                    self.m[v] = self.y[v]*self.m[i]
                elif self.m[v] != '-':
                    self.m[i] = self.m[v]/self.y[v]
                    self.m[l] = self.m[i] - self.m[v]
        else:
            if self.m[l] == '-':
                if self.m[v] == '-':
                    self.m[v] = (self.h[i]*self.m[kargs[0]] + self.h[j]*self.m[kargs[1]] - self.h[l]*(self.m[kargs[0]]+self.m[kargs[1]]))/(self.h[v]-self.h[l])
                    self.m[l] = self.m[kargs[0]] + self.m[kargs[1]] - self.m[v]
                if self.m[kargs[0]] == '-':
                    self.m[kargs[0]] = (self.h[v]*self.m[v] - self.h[kargs[1]]*self.m[kargs[1]] + self.h[l]*(self.m[kargs[1]]-self.m[v]))/(self.h[kargs[0]]-self.h[l])
                    self.m[l] = self.m[kargs[0]] + self.m[kargs[1]] - self.m[v]
                if self.m[kargs[1]] == '-':
                    self.m[kargs[1]] = (self.h[v]*self.m[v] - self.h[kargs[0]]*self.m[kargs[0]] + self.h[l]*(self.m[kargs[0]]-self.m[v]))/(self.h[kargs[1]]-self.h[l])
                    self.m[l] = self.m[kargs[0]] + self.m[kargs[1]] - self.m[v]
            if self.m[v] == '-':
                if self.m[kargs[0]] == '-':
                    self.m[kargs[0]] = (self.h[l]*self.m[l] - self.h[kargs[1]]*self.m[kargs[1]] + self.h[v]*(self.m[kargs[1]]-self.m[l]))/(self.h[kargs[0]]-self.h[v])
                    self.m[v] = self.m[kargs[0]] + self.m[kargs[1]] - self.m[l]
                if self.m[kargs[1]] == '-':
                    self.m[kargs[1]] = (self.h[l]*self.m[l] - self.h[kargs[0]]*self.m[kargs[0]] + self.h[v]*(self.m[kargs[0]]-self.m[l]))/(self.h[kargs[1]]-self.h[v])
                    self.m[v] = self.m[kargs[0]] + self.m[kargs[1]] - self.m[l]

    def SetMass(self,i,m):
        self.m[i] = m

    def Tub(self,*kargs):
        for i in kargs:
            if self.y[i] != '-':
                ft = self.y[i]
                for i in kargs:
                    self.y[i] = ft 
            if self.m[i] != '-':
                mf = self.m[i]
                for i in kargs:
                    self.m[i] = mf

    def Exibir(self,*kargs):
        for j in kargs:
            if j == 'h':
                hp=['Entalpia (kJ/kg):']
                for i in range(1,len(self.h)):
                    if self.h[i] == '-':
                        hp.append('-')
                    else:
                        hp.append(round(self.h[i],2))
                print(hp)
            if j == 'p':
                pp=['Pressao (kPa):']
                for i in range(1,len(self.p)):
                    if type(self.p[i]) == str:
                        pp.append(self.p[i])
                    else:
                        pp.append(round(self.p[i],2))
                print(pp)
            if j == 's':
                sp = ['Entropia (kJ/kgK)']
                for i in range(1,len(self.s)):
                    if type(self.s[i]) == str:
                        sp.append(self.s[i])
                    else:
                        sp.append(round(self.s[i],3))
                print(sp)        
            if j == 'T':
                Tp =['Temperatura (K):']
                for i in range(1,len(self.T)):
                    if self.T[i] == '-':
                        Tp.append('-')
                    else:
                        Tp.append(round(self.T[i],2))
                print(Tp)
            if j == 'x':
                xp = ['Titulo']
                for i in range(1,len(self.x)):
                    if self.x[i] == '-':
                        xp.append('-')
                    else:
                        xp.append(round(self.x[i],3))
                print(xp)
            if j == 'y':
                yp = ['Fracao massica']
                for i in range(1,len(self.y)):
                    if self.y[i] == '-':
                        yp.append('-')
                    else:
                        yp.append(round(self.y[i],2))
                print(yp)
            if j == 'm':
                mp = ['Vazao massica']
                for i in range(1,len(self.m)):
                    if self.m[i] == '-':
                        mp.append('-')
                    else:
                        mp.append(round(self.m[i],3))
                print(mp)
            if j == 'q':
                qp = {}
                for i in self.q:
                    qp[i] = round(self.q[i],2)
                print(qp)
            if j == 'wb':
                wbp = {}
                for i in self.wb:
                    wbp[i] = round(self.wb[i],2)
                print(wbp)
            if j == 'wt':
                wtp = {}
                for i in self.wt:
                    wtp[i] = round(self.wt[i],2)
                print(wtp)
            if j == 'wc':
                wcp = {}
                for i in self.wc:
                    wcp[i] = round(self.wc[i],2)
                print(wcp)

    def TCT(self,t,c):
        mt, mos, mic, hic, his, hos, hot = symbols('mt mos mic hic his hos hot')
        mc = Eq(mic + mt - mos, 0)
        ec = Eq(mt*hot + mos*hos -mt*hic - mic*hic - mt*his, 0)
        dados = [('hos',self.h[c])]
        var = []
        if t == 2:
            dados.append(('hic',self.h[t-3]))
            if self.m[t] == '-':
                var.append('mt')
            else:
                dados.append(('mt',self.m[t]))
            if self.m[t-1] == '-':
                var.append('mic')
            else:
                dados.append(('mic',self.m[t-1]))
            if self.h[t] == '-':
                var.append('hot')
            else:
                dados.append(('hot',self.h[t]))
        elif t == 1:
            dados.append(('hic',self.h[t-3]))
            if self.m[t] == '-':
                var.append('mt')
            else:
                dados.append(('mt',self.m[t]))
            if self.m[t-1] == '-':
                var.append('mic')
            else:
                dados.append(('mic',self.m[t-2]))
            if self.h[t] == '-':
                var.append('hot')
            else:
                dados.append(('hot',self.h[t]))
        else:
            dados.append(('hic',self.h[t-2]))
            if self.m[t] == '-':
                var.append('mt')
            else:
                dados.append(('mt',self.m[t]))
            if self.m[t-1] == '-':
                var.append('mic')
            else:
                dados.append(('mic',self.m[t-1]))
            if self.h[t] == '-':
                var.append('hot')
            else:
                dados.append(('hot',self.h[t]))
        dados.append(('hos',self.h[c]))
        if c == 1:
            if self.h[c-2] == '-':
                var.append('his')
            else:
                dados.append(('his',self.h[c-2]))
        else:
            if self.h[c-1] == '-':
                var.append('his')
            else:
                dados.append(('his',self.h[c-1]))
        if self.m[c] == '-':
            var.append('mos')
        else:
            dados.append(('mos',self.m[c]))
        sol = solve((mc.subs(dados),ec.subs(dados)),var)
        for k in sol:
            if k == mic:
                if t == 1:
                    self.m[t-2] = sol[k]
                else:
                    self.m[t-1] = sol[k]
            if k == mos:
                self.m[c] = sol[k]
            if k == mt:
                self.m[t] = sol[k]
                if t == 2:
                    m[t-3] = sol[k]
                else:
                    m[t-2] = sol[k]
                if c == 1:
                    m[c-2] = sol[k]
                else:
                    m[c-1] = sol[k]
        print(sol)

    def COP(self,l):
        if self.m[l] != '-':
            Cop = self.q[l]*self.m[l]/self.TrabC()
        elif self.y[l] != '-':
            Cop = self.q[l]*self.y[l]/self.TrabC()
        else:
            Cop = self.q[l]/self.TrabC
            print('Calculo do COP realizado supondo unico fluxo')
        print(f'COP Calculado do ciclo: {round(Cop,3)}')