# Introduction to Periodic-Frequent Pattern Mining using PAMI 


Technological advances in the field of Information and Communication Technologies have enabled organizations to collect big data. Useful information that can empower the end-users to achieve socio-economic development lies hidden in these databases. The field of pattern mining emerged to discover interesting information in very large databases. Pattern mining aims to discover interesting patterns (or itemsets) that may exist in a database. Pattern mining techniques were extended to other knowledge discovery techniques, such as clustering, classification, and recommender systems, to improve their performance significantly. Some of the popular pattern mining techniques are frequent pattern mining, correlated pattern mining, utility pattern mining, and periodic-frequent patterns. In this tutorial, we first describe periodic-frequent pattern mining with an illustrative example. Second, we discuss the search space and list the available algorithms. Third, we introduce the PAMI package and explain how to employ the mining algorithms to find desired patterns. Finally, we describe the merits and demerits of this mining technique followed by the extended versions of this technique.


### What is Periodic-Frequent Pattern Mining?
Periodic-frequent patterns are an important class of regularities that exist in a temporal database. A periodic-frequent pattern indicates that there exists something that is predictable with the database. Henceforth, there exists value in finding these patterns in real-world applications. The objective of periodic-frequent pattern mining is to discover all patterns that are both frequent and periodic within the database. A classic application of these patterns is air pollution analytics. It involves identifying the locations in which people were regularly exposed to harmful levels of an air pollutant, say PM2.5.

Figure 1: Application of periodic-frequent pattern mining on air pollution data 
![Application of periodic-frequent patterns](periodicFrequentPattern.jpg?raw=true "Fig 1. Identifying the locations in which people were regularly exposed to harmful levels of PM2.5 in Japan")

__Example:__ Air pollution is the major cause of many cardio-respiratory problems reported in Japan. On average, 42.6 thousand people are dying every year in Japan due to pollution. To tackle this problem, a nationwide sensor network, called SORAMAME (Atmospheric Environmental Regional Observation System: AEROS), was set up by the Ministry of Environment, Japan, to monitor pollution. Figure 1a shows the spatial locations of these sensors in Japan. The raw data (see Figure 1b) generated by this system for an air pollutant at hourly intervals can be represented as a temporal database (see Figure 1c). Periodic-frequent pattern mining (see Figure 1c) on this database provides the environmentalists and policymakers with useful information regarding the areas (see Figure 1d & 1e) in which people were regularly exposed to harmful levels of air pollution.


Table 1: A temporal database
![Temporal database](tdb.jpg?raw=true "Table 1. Temporal database")


Let *\{S1, S2, S3, S4, S5, S6\}* be a set of air pollution measuring sensors.  Table 1 shows a hypothetical air pollution
temporal database generated by these sensors. This database contains 12 transactions. The __initial timestamp__ of this database, i.e., *ts<sub>initial</sub>=0*. 
The __final timestamp__ of this database, i.e., *ts<sub>final</sub>=15*. The first transaction in this database provides the information that the 
sensors *S1, S2* and *S5* have recorded hazardous levels of PM2.5. Other transactions in this database can explained in the similar fashion.
The set of sensors, *S1* and *S2*, i.e., *\{S1,S2\}*, is called a pattern (or an itemset). In Table 1, this pattern occurs at the
timestamps of 1, 3, 6, 8, 9, 12 and 14. Thus, the *support* (or *frequency*) of \{S1,S2\} is 7. If the user-specified *minimum support*, denoted as *minSup*, is 5, then *\{S1,S2\}* is said to be a __frequent pattern__. 
The *periods* of this pattern are: 1 (=1-ts<sub>initial</sub>), 2 (=3-1), 3 (=6-3), 2 (=8-6), 1 (=9-8), 3 (=12-9), 2 (=14-12) and 1 (=ts<sub>final</sub>-14). The maximum *period* of this pattern is considered as its *periodicity*. Thus, the *periodicity* of 
*\{S1,S2\}*, i.e., *per(\{S1,S2\})=max(1,2,3,2,1,3,2,1) = 3*. It means the sensors *S1* and *S2* have simultaneously recorded hazardous levels of PM2.5 at least once in every 3 hours.
If the user-specified *maximum periodicity* (*maxPer*) is 3, then the frequent pattern *\{S1,S2\}* is said to be a periodic-frequet pattern. This pattern is expressed as follows: 

      {S1,S2}   [support=7, periodicity=3]

## What are the algorithms available for finding periodic-frequent patterns?
The space of items in an itemset lattice represents the search space of periodic-frequent pattern mining. Thus, the search space of periodic-frequent pattern mining is *2<sup>n</sup>-1*, where *n* represents the total number of items in a database.
The mining algorithms reduce this huge search space by employing __apriori/anti-monotonic/downward-closure property__. This property says that "*all non-empty subsets of a periodic-frequent pattern are also periodic-frequet patters*." This property makes the pattern mining practicable on real-world large databases.
The algorithms to discover periodic-frequent patterns are: PFP-growth, PFP-growth++, PS-growth and PFP-ECLAT.

## What is PAMI? How to install and implement the periodic-frequent pattern mining algorithm in PAMI?
PAMI stands for PAttern MIning.  It is a Python library containing several pattern mining algorithms. This library is supplied under GPL V3 liscence. 
Install this library by executing the following command:
 
    pip install pami


The good thing about the PAMI library is that items in the database can be integers or strings.  For illustrative purposes, we use the temporalAirPollution database available at [download](). Users can also try with other datasets. However, please keep in mind that the temporal database
must exist in the following format:

    timestamp<sep>item1<sep>item2<sep>...<sep>itemN

The separator can be tab space (default), comma, space, etc. 
Several algorithms exist in PAMI library to find periodic-frequent patterns.  For brevity, we employ PS-growth algorithm to find periodic-frequent patterns.

Step 1: Import the PS-growth algorithm from PAMI library

    from PAMI.periodicFrequentPattern.basic import PSGrowth as alg

Step 2: Initialize and execute the mining algorithm by passing the data, minSup and maxPer parameters. Please note that data can be a http link, a file, or a data frame.

    URL="https://www.u-aizu.ac.jp/~udayrage/datasets/temporalDatabases/temporal_T10I4D100K.csv"
    obj = alg.PSGrowth(iFile=URL,minSup=20,maxPer=100)   #initialization
    obj.mine()                                      #execution of the algorithm

Step 3: Store the patterns in a file

    obj.save('patterns.txt')

Step 4: Printing the patterns

    df = obj.getPatternsAsDataFrame()
    df

Step 5: Calculating number of patterns, memory, and runtime

    print(len(df))
    print(obj.getMemoryRSS())
    print(obj.getRuntime())

Step 6: (Visualization) Selecting top-k long patterns and displaying them