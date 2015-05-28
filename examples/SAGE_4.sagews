︠b85a5dd2-e00f-4dbb-83e1-bffc3c2ef153︠

︡ccfcf840-67af-4bd8-bebd-18a901feb806︡
︠af523b37-267e-4537-89e6-373516e636f9si︠
%md
# Ejercicios de pruebas anteriores.
︡90f7df06-d255-4065-9953-defa37135b98︡{"md":"# Ejercicios de pruebas anteriores.\n"}︡
︠fa647f5d-df1a-429b-9067-12aa67f38fb2is︠
%md
En todos los ejercicios,  `F` será $\mathbb{F}_{27}=\mathbb{F}_{3}[\alpha]=$ el cuerpo de $27$ elementos, dado como una  extensión algebraica de $\mathbb{F}_{3}$. 
︡e82b2fce-3775-4234-aedf-3c10f3474697︡{"md":"En todos los ejercicios,  `F` será $\\mathbb{F}_{27}=\\mathbb{F}_{3}[\\alpha]=$ el cuerpo de $27$ elementos, dado como una  extensión algebraica de $\\mathbb{F}_{3}$. \n"}︡
︠a8cf427c-c2fb-48eb-8ad7-e2c47a6ebf4ais︠
%md
**Ejercicio 0**
Responda (con código)  a las siguientes cuestiones:
1. Calcule $\varphi(2887465412)$.
2. Calcule el cociente y el resto de la división euclídea de $ 5416816541$ entre $78214$.
3. Dé el máximo común divisor y una identidad de Bézout de los enteros $541968416909$ y $2^{34}$.

︡468817cd-2e92-41f9-a31a-d4f3ae100326︡{"md":"**Ejercicio 0**\nResponda (con código)  a las siguientes cuestiones:\n1. Calcule $\\varphi(2887465412)$.\n2. Calcule el cociente y el resto de la división euclídea de $ 5416816541$ entre $78214$.\n3. Dé el máximo común divisor y una identidad de Bézout de los enteros $541968416909$ y $2^{34}$.\n\n"}︡
︠078f37d7-89b6-4c35-b699-3640cfc758d8s︠
# 0.1
euler_phi(2887465412)
︡94d71648-251c-47b7-bb4b-364f9e612ea8︡{"stdout":"1332676320\n"}︡
︠acbbf7f1-5b34-47f6-9755-b17898348e4bs︠
# 0.2 
ZZ(5416816541).quo_rem(78214)
︡487dd3b2-3550-41de-b576-8117bd1fed79︡{"stdout":"(69256, 27757)\n"}︡
︠18116fa3-b2b2-4e8d-bb96-bb4880f3c2c9s︠
# 0.3 
a=541968416909
b=2^34
d,alpha,beta=xgcd(a,b)
d==alpha*a+beta*b
︡1e262d3a-20eb-413d-995e-fdd0fadb9d75︡{"stdout":"True\n"}︡
︠16df9455-246c-4591-9637-24a11ffc7a80si︠
%md
**Ejercicio 1**

   1. Defina $\mathbb{F}_{27}$ en SAGE, y dé el polinomio mínimo de $\alpha$.
   2. Sabiendo que `F.list()` es una lista de los elementos del cuerpo finito (¡incluyendo el cero!), calcule una lista con las parejas de cada elemento no nulo y su inverso. 
   
︡e12334f8-205b-4833-8146-7b808f5d9e67︡{"md":"**Ejercicio 1**\n\n   1. Defina $\\mathbb{F}_{27}$ en SAGE, y dé el polinomio mínimo de $\\alpha$.\n   2. Sabiendo que `F.list()` es una lista de los elementos del cuerpo finito (¡incluyendo el cero!), calcule una lista con las parejas de cada elemento no nulo y su inverso. \n   \n"}︡
︠793c7067-b4cc-4414-9046-c393396f7325s︠
# 1.1
F27.<a>=GF(27)
︡65f7ab5e-cf2a-4bba-bf93-8b1443d970e4︡
︠0e2cebcf-e015-412c-9d77-9cfbfa4cd331s︠
# 1.2 +1.2
[(a,a^(-1)) for a in F27.list() if a!=0]
︡aaf999b1-6d06-4c8b-b741-d7f1cd776de5︡{"stdout":"[(a, 2*a^2 + 1), (a^2, 2*a^2 + 2*a + 1), (a + 2, 2*a^2 + 2*a), (a^2 + 2*a, 2*a + 2), (2*a^2 + a + 2, a^2 + 1), (a^2 + a + 1, 2*a^2 + a + 1), (a^2 + 2*a + 2, 2*a^2 + 2*a + 2), (2*a^2 + 2, a^2 + 2*a + 1), (a + 1, 2*a^2 + a), (a^2 + a, 2*a + 1), (a^2 + a + 2, 2*a^2), (a^2 + 2, 2*a), (2, 2), (2*a, a^2 + 2), (2*a^2, a^2 + a + 2), (2*a + 1, a^2 + a), (2*a^2 + a, a + 1), (a^2 + 2*a + 1, 2*a^2 + 2), (2*a^2 + 2*a + 2, a^2 + 2*a + 2), (2*a^2 + a + 1, a^2 + a + 1), (a^2 + 1, 2*a^2 + a + 2), (2*a + 2, a^2 + 2*a), (2*a^2 + 2*a, a + 2), (2*a^2 + 2*a + 1, a^2), (2*a^2 + 1, a), (1, 1)]\n"}︡
︠ed78e109-e024-4800-ae4d-0f666a0a7ae5si︠
%md
**Ejercicio 2**

En el anillo de polinomios con coeficientes en `F`,
   1. Factorice el polinomio $x^{11}-x$. 
   2. Calcule la identidad de Bézout para $f(x)=x^4 + x^3 + x^2 + x + 1$ y $g(x)=x^{2}+x+9\alpha$.
︡dcf42eca-24eb-4570-aef7-393f94db283f︡{"md":"**Ejercicio 2**\n\nEn el anillo de polinomios con coeficientes en `F`,\n   1. Factorice el polinomio $x^{11}-x$. \n   2. Calcule la identidad de Bézout para $f(x)=x^4 + x^3 + x^2 + x + 1$ y $g(x)=x^{2}+x+9\\alpha$.\n"}︡
︠2f1c218a-327d-452a-afb9-a5042680f7ae︠
# 2.1
R.<x>=PolynomialRing(F27)
f=x^11-x
f.factor()
︡25d5fa2c-f549-46f2-9ebd-1d5b83362472︡{"stdout":"x * (x + 1) * (x + 2) * (x^4 + x^3 + x^2 + x + 1) * (x^4 + 2*x^3 + x^2 + 2*x + 1)\n"}︡
︠069eba30-3eac-4185-898f-94db648b72f4s︠
# 2.2
f=x^4+x^3+x^2+x+1
g=x^2+x+9*a
xgcd(f,g)
     
︡3b0a6976-3e25-4672-b3cf-8a505bd5e833︡{"stdout":"(1, 1, 2*x^2 + 2)\n"}︡
︠58bb28c2-4a37-452b-8002-9eb0a1314705︠
︡af9350cf-b90e-4c2d-82e9-31bf147ea3c4︡
︠7af57813-1e1b-4e28-9476-2b283e072f99si︠
%md
**Ejercicio 3 **

Calcule, en $\mathbb{F}_{27}$ un polinomio $h(x)$ tal que
\[
\begin{cases}
h(x)\equiv x-\alpha & \pmod{f(x)}\\
h(x)\equiv x^{2}-\alpha & \pmod{g(x)}
\end{cases}
\]  
(Los polinomios $f$ y $g$ son los del ejercicio anterior.)
︡c0be745f-bb3e-40c7-988f-536aa97de132︡{"md":"**Ejercicio 3 **\n\nCalcule, en $\\mathbb{F}_{27}$ un polinomio $h(x)$ tal que\n\\[\n\\begin{cases}\nh(x)\\equiv x-\\alpha & \\pmod{f(x)}\\\\\nh(x)\\equiv x^{2}-\\alpha & \\pmod{g(x)}\n\\end{cases}\n\\]  \n(Los polinomios $f$ y $g$ son los del ejercicio anterior.)\n"}︡
︠74a94175-666d-4229-b231-b81061543c13s︠
# 3
crt([x-a, x ^2-a],[f,g])
︡78f04e7c-ffc6-46b5-9f65-f0fa56a4f95e︡{"stdout":"x^5 + x^4 + x^3 + x^2 + 2*x + 2\n"}︡
︠7767199c-592f-49c9-831e-b2a89cd5016b︠

︡a9984032-d02b-420b-b3aa-5a0056d5751c︡
︠efe860de-78af-4730-bbde-6e491d532345si︠
%md
**Ejercicio 4**
Defina una función `fi(n)` que calcule $\phi(n)$ por el procedimiento de contar los números menores que $n$ coprimos con $n$. Calcule $\varphi(10)$.
︡c66d95b1-b8b2-490f-96ce-c6c7d4b4c980︡{"md":"**Ejercicio 4**\nDefina una función `fi(n)` que calcule $\\phi(n)$ por el procedimiento de contar los números menores que $n$ coprimos con $n$. Calcule $\\varphi(10)$.\n"}︡
︠bba4da0e-7593-44a1-b3e7-cc7db9f988b0s︠
# 4
def fi(n):
    return len([1 for i in [1..n] if gcd(i,n)==1])
fi(10)
︡37053936-0827-4e79-a255-4df5b442acf7︡{"stdout":"4\n"}︡
︠e7c502b7-7478-490e-a610-19037c7b5153︠

︡84c53352-d82e-4038-bfd4-446760d813c6︡
︠cc6eae2a-e455-4b5d-9d0c-c96f3d3d4e76si︠
%md
**Ejercicio 5**


1. Factorice el polinomio $X^7 −X^6 −17X^5 +X^4 −16X^2 +336^X −144$ sobre los cuerpos $\mathbb{Q}$, $\mathbb{F}_3$, $\mathbb{F}_{27}$.

2. Escriba una función `factorizar_sobre(f,p,r)`, que dado un polinomio `f`, un primo `p` y un exponente `r`, devuelva la factorización de `f` sobre $\mathbb{F}_{p^r}$. Será necesario definir el anillo correspondiente dentro de la función.
︡06045a40-dfa9-454f-beac-9b7f49a54956︡{"md":"**Ejercicio 5**\n\n\n1. Factorice el polinomio $X^7 −X^6 −17X^5 +X^4 −16X^2 +336^X −144$ sobre los cuerpos $\\mathbb{Q}$, $\\mathbb{F}_3$, $\\mathbb{F}_{27}$.\n\n2. Escriba una función `factorizar_sobre(f,p,r)`, que dado un polinomio `f`, un primo `p` y un exponente `r`, devuelva la factorización de `f` sobre $\\mathbb{F}_{p^r}$. Será necesario definir el anillo correspondiente dentro de la función.\n"}︡
︠140aed71-23d8-43d5-8aaf-a1f4b4408cb9s︠
# 5
R.<X>=PolynomialRing(QQ)
f=X^7-X^6-17*X^5+X^4-16*X^2+336*X-144
f.factor()
︡21aada11-2239-403d-90e7-b9df8fd5d450︡{"stdout":"(X - 2) * (X + 3)^2 * (X^2 - 5*X + 2) * (X^2 + 4)\n"}︡
︠44821ccf-2a8e-4c54-97d0-c5f7b06d6a78s︠
R.<X>=PolynomialRing(GF(3))
f=X^7-X^6-17*X^5+X^4-16*X^2+336*X-144
f.factor()
︡b59b1d68-6f32-4105-b9d7-05d959ed915a︡{"stdout":"(X + 1) * X^2 * (X^2 + 1) * (X^2 + X + 2)\n"}︡
︠ffaede2c-cd96-40ce-a6d6-b5a1a4bb5fd7s︠
R.<X>=PolynomialRing(F27)
f=X^7-X^6-17*X^5+X^4-16*X^2+336*X-144
f.factor()
︡f28c3d45-0aac-4d9e-a2a3-f0ec95355812︡{"stdout":"(X + 1) * X^2 * (X^2 + 1) * (X^2 + X + 2)\n"}︡
︠68216a32-25d2-4be1-8ab7-a4f44a24a238si︠
%md
** Ejercicio 6**

Crear un procedimiento, llamado `mcd`, que reciba un entero positivo $n$, y devuelva una lista de sublistas que contengan, por cada entero entre $1$ y $n$:

1. El propio número y la cadena `"coprimo"`, si es primo con $n$.

2. El propio número y el máximo común divisor de n con él, en otro caso. 

Por ejemplo:

    mcd(6)−→[[1,’coprimo’],[2,2],[3,3],[4,2],[5,’coprimo’],[6,6]]
︡14f3cffd-5062-4999-a830-36b89453b403︡{"md":"** Ejercicio 6**\n\nCrear un procedimiento, llamado `mcd`, que reciba un entero positivo $n$, y devuelva una lista de sublistas que contengan, por cada entero entre $1$ y $n$:\n\n1. El propio número y la cadena `\"coprimo\"`, si es primo con $n$.\n\n2. El propio número y el máximo común divisor de n con él, en otro caso. \n\nPor ejemplo:\n\n    mcd(6)−→[[1,’coprimo’],[2,2],[3,3],[4,2],[5,’coprimo’],[6,6]]\n"}︡
︠fcd16716-c29b-48e4-ba20-334148695469s︠
def mcd(n):
    return [ [i, 'coprimo' if gcd(i,n)==1 else gcd(i,n)] for i in [1..n] ]
︡ca213581-6cd7-4491-ba74-d21ce7bf711b︡
︠9697d179-72bf-4fa6-88a0-aba30d783125s︠
mcd(6)
︡53fc2f8a-0e7c-47c0-9a73-ef7760171f1b︡{"stdout":"[[1, 'coprimo'], [2, 2], [3, 3], [4, 2], [5, 'coprimo'], [6, 6]]\n"}︡
︠a7691ebd-5ca3-489b-991f-f0f1c3a25e20︠
︡b8f8db6f-a449-4446-a14a-897936e7d5ae︡
︠1afa06f9-7013-488c-9646-22fbebf85515︠









