#include <iostream>
#include <chrono>
#include <algorithm>
#include <random>
#include <thread>
#include <mutex>

std::mutex mtx;

struct vec
{
    long int* array;
    long int len;
};

void mergeSortT(vec &ret, vec &arr, long int st, long int en);
vec mergeSortMT(vec &arr, long int st, long int en);

int thread_const = 1000000;

void merge(vec &ret, long int &length, vec &a, vec &b)
{
    ret.array = new long int[length+1];
    ret.len = length+1;
    long int a_c = 0;
    long int b_c = 0;
    
    while (true)
    {
        if(a.array[a_c] < b.array[b_c])
        {
            ret.array[a_c + b_c] = a.array[a_c];
            a_c++;
            if(a_c >= a.len)
            {
                while (b_c < b.len)
                {
                    ret.array[a_c + b_c] = b.array[b_c];
                    b_c++;
                }
                break;
            }
        }
        else
        {
            ret.array[a_c + b_c] = b.array[b_c];
            b_c++;
            if(b_c >= b.len)
            {
                while (a_c < a.len)
                {
                    ret.array[a_c + b_c] = a.array[a_c];
                    a_c++;
                }
                break;
            }
        }
    }
    delete[] a.array;
    delete[] b.array;
}

void mergeSortT(vec &ret, vec &arr, long int st, long int en)
{
    long int length = en - st;
    if(length == 0)
    {
        ret.array = new long int[1]{arr.array[st]};
        ret.len = 1;
    }
    else if(length == 1)
    {
        if(arr.array[en] < arr.array[st])
        {
            long int tmp = arr.array[st];
            arr.array[st] = arr.array[en];
            arr.array[en] = tmp;
        }
        ret.array = new long int[2]{arr.array[st], arr.array[en]};
        ret.len = 2;
    }
    else if(length > 1)
    {
        long int dev = length/2;
        if(length > thread_const)
        {
            vec a;
            vec b;
            std::thread th1 (mergeSortT, std::ref(a), std::ref(arr), st, st+dev);
            std::thread th2 (mergeSortT, std::ref(b), std::ref(arr), st+dev+1, en);
            th1.join();
            th2.join();
            merge(ret, length, a, b);
        }
        else
        {
            vec a = mergeSortMT(arr, st, st+dev);
            vec b = mergeSortMT(arr, st+dev+1, en);
            merge(ret, length, a, b);
        }   
    }
}

vec mergeSort(vec &arr, long int st, long int en)
{
    long int length = en - st;
    vec ret = vec();
    if(length == 0)
    {
        ret.array = new long int[1]{arr.array[st]};
        ret.len = 1;
    }
    else if(length == 1)
    {
        if(arr.array[en] < arr.array[st])
        {
            long int tmp = arr.array[st];
            arr.array[st] = arr.array[en];
            arr.array[en] = tmp;
        }
        ret.array = new long int[2]{arr.array[st], arr.array[en]};
        ret.len = 2;
    }
    else if(length > 1)
    {
        long int dev = length/2;
        vec a = mergeSort(arr, st, st+dev);
        vec b = mergeSort(arr, st+dev+1, en);
        
        ret.array = new long int[length+1];
        ret.len = length+1;

        long int a_c = 0;
        long int b_c = 0;
        
        while (true)
        {
            if(a.array[a_c] < b.array[b_c])
            {
                ret.array[a_c + b_c] = a.array[a_c];
                a_c++;
                if(a_c >= a.len)
                {
                    while (b_c < b.len)
                    {
                        ret.array[a_c + b_c] = b.array[b_c];
                        b_c++;
                    }
                    break;
                }
            }
            else
            {
                ret.array[a_c + b_c] = b.array[b_c];
                b_c++;
                if(b_c >= b.len)
                {
                    while (a_c < a.len)
                    {
                        ret.array[a_c + b_c] = a.array[a_c];
                        a_c++;
                    }
                    break;
                }
            }
        }
        delete[] a.array;
        delete[] b.array;
    }
    return ret;
}

vec mergeSortMT(vec &arr, long int st, long int en)
{
    long int length = en - st;
    vec ret = vec();
    if(length == 0)
    {
        ret.array = new long int[1]{arr.array[st]};
        ret.len = 1;
    }
    else if(length == 1)
    {
        if(arr.array[en] < arr.array[st])
        {
            long int tmp = arr.array[st];
            arr.array[st] = arr.array[en];
            arr.array[en] = tmp;
        }
        ret.array = new long int[2]{arr.array[st], arr.array[en]};
        ret.len = 2;
    }
    else if(length > 1)
    {
        long int dev = length/2;
        if(length > thread_const)
        {
            vec a;
            vec b;
            std::thread th1 (mergeSortT, std::ref(a), std::ref(arr), st, st+dev);
            std::thread th2 (mergeSortT, std::ref(b), std::ref(arr), st+dev+1, en);
            th1.join();
            th2.join();
            merge(ret, length, a, b);
        }
        else
        {
            vec a = mergeSortMT(arr, st, st+dev);
            vec b = mergeSortMT(arr, st+dev+1, en);
            merge(ret, length, a, b);
        }   
    }
    return ret;
}



int main()
{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long int> distrib(0,100000000000);
    int arr_length = 100000000;

    vec arr = vec();
    arr.array = new long int [arr_length];
    arr.len = arr_length;

    for(long int i = 0; i < arr_length; i++)
    {
        arr.array[i] = distrib(gen);
    }
    
    std::cout << "start" << std::endl;

    std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
    vec sorted_array = mergeSortMT(arr, 0, arr.len-1);
    std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double, std::milli> time_span = t2 - t1;

    std::cout << "duration " << time_span.count() << std::endl;

    for(long int i = 0; i < sorted_array.len; i++)
    {
        std::cout << sorted_array.array[i] << " " << std::flush;
    }
    std::cout << std::endl;


    delete[] arr.array;
    delete[] sorted_array.array;

    return 0;
}
