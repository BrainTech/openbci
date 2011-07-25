To prepare system:
1. download svarog master revision efbaf1e45141d1647f779a8f31836473e1b5c229
2. apply patch by: git apply svarog_profiling_patch_efbaf1e45141d1647f779a8f31836473e1b5c229.txt
3. run mvn clean && mvn compile && mvn exec:java
4. Open 'montage' dialog 
5. Import predefined montage profiling_50


To run profiling:
1. Fire amplifier with 50 channels and the last channel being SAMPLE_NUMBER channel, eg use: ../cpp/run_mx_amplifier 50 1024 1234 1
2. Connect to MX in Svarog, load montage profiling_50

OR

1. Fire some other amplifier with number_of_channels > 10 and last channel being sample number
2. Connect to MX in svarog (don`t use profiling_50)


