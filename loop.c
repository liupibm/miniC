int sumUp(int arg){
    int sum = 0;
    int i=0;
    while(i<arg){
        sum = sum + i*2;
        i++;
    }

    return sum;

}

int main () {
    int result = sumUp(10);
    printf("%d", result);
}
