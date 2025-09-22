% Факты
parent(pam, bob).
parent(tom, bob).
parent(tom, liz).
parent(bob, ann).
parent(bob, pat).
parent(mary, ann).
parent(pat, juli).

male(tom).
male(bob).
male(jim).
female(liz).
female(pam).
female(pat).
female(ann).
female(mary).
female(juli).

% Правила
child(Y, X) :- parent(X, Y).

mother(X, Y) :- parent(X, Y), female(X).

father(X, Y) :- parent(X, Y), male(X).

grandmother(X, Y) :- parent(X, Z), parent(Z, Y), female(X).

grandfather(X, Y) :- parent(X, Z), parent(Z, Y), male(X).

brother(X, Y) :- parent(Z, X), parent(Z, Y), male(X).

sister(X, Y) :- parent(Z, X), parent(Z, Y), female(X).

uncle(X, Y) :- brother(X, Z), parent(Z, Y).

aunt(X, Y) :- sister(X, Z), parent(Z, Y).
