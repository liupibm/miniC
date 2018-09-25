int maxInt(int arg1, int arg2){
    if(arg1<arg2)
        return arg2;
    else
        return arg1;

}

int main () {
    int max = maxInt(3,5);
    printf("%d", max);

}
