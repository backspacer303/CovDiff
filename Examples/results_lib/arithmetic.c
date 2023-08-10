#include "arithmetic.h"

double sub(double a, double b){
    return a-b;
}
double mul(double a, double b){
    return a*b;
}

double add(double a, double b){
    return a+b;
}

double max(double a, double b){
    if(a>=b)
        return a;
    else
        return b;
}
