#include <iostream>
#include <ctime>

using namespace std;

void
swap(int &a, int &b)
{
    int tmp = a;
    a = b;
    b = tmp;
}

void
bubble_sort(int *a, int size)
{
    int i = 0;
    int j = 0;
    int tmp = 0;

    for (i = 0; i < size - 1; i++)
    {
        for (j = 0; j < size - 1 - i; j++)
        {
            if (a[j] < a[j+1])
            {
                swap(a[j], a[j+1]);
            }
        }
    }
}

void
bubble_based_shuffle(int *a, int size)
{
    int i = 0;
    int j = 0;
    int tmp = 0;

    for (i = 0; i < size - 1; i++)
    {
        for (j = 0; j < size - 1 - i; j++)
        {
            if ((a[j] + a[j+1]) % 2 == 0)
            {
                swap(a[j], a[j+1]);
            }
        }
    }
}

void
random_shuffle(int *a, int size)
{
    int i = 0;
    int index = 0;
    srand((unsigned)time(0));

    for(i = 0; i < size; i++)
    {
        index = rand() % (size-i) + i;
        swap(a[i], a[index]);
    }
}

void
print(int *a, int size)
{
    int i = 0;
    for (i = 0; i < size; i++)
    {
        cout << a[i] << ", " << endl;
    }
    cout << endl;
}

int main(void)
{
    int a[] = {8, 2, 6, 3, 4, 5, 9, 0, 1, 7};
    bubble_based_shuffle(a, 10);
    print(a, 10);
    bubble_sort(a, 10);
    print(a, 10);
    random_shuffle(a, 10);
    print(a, 10);

    return 0;
}
