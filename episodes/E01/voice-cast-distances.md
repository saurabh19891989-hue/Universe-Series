# E01 voice-cast fingerprint distances

Distance = weighted, z-scored (over all 53 Kokoro voices) difference of median f0, f0 range, spectral centroid, speaking rate and 12 MFCC means on one fixed sentence, measured after the pitch/speed/band treatment. Larger = easier to tell apart by these measures. These are not listening results; nobody has listened.

## Chosen cast

| role | voice | speed | pitch | formant | f0 median Hz | f0 range Hz | centroid Hz | rate words/s |
|---|---|---|---|---|---|---|---|---|
|JAX|am_puck|1.08|1.0|preserved|106|105|1130|3.65|
|PIP|bm_george|1.05|1.0|preserved|142|54|1025|3.17|
|BARON|bm_fable|0.9|0.93|preserved|112|67|1458|3.41|
|CHICHIKOV|am_michael|0.9|1.0|preserved|116|62|1093|2.82|
|NOAKES|bm_daniel|1.15|1.1|shifted|135|49|1042|3.84|
|MIRA|bf_alice|0.95|0.9|preserved|194|120|1550|3.36|
|LUCÍA|af_bella|1.1|1.0|preserved|211|78|1576|3.29|
|TEMI|af_jessica|1.08|1.02|preserved|216|116|1439|3.91|
|MAMANI|am_eric|0.95|1.0|preserved|159|90|835|3.76|

## Pairwise distances, new cast (min 2.19, mean 3.83)

| |JAX|PIP|BARON|CHICHIKOV|NOAKES|MIRA|LUCÍA|TEMI|MAMANI|
|---|---|---|---|---|---|---|---|---|---|
|**JAX**||3.2|2.5|3.0|2.8|4.3|5.2|4.9|3.2|
|**PIP**|3.2||2.9|2.4|2.2|4.5|4.2|4.8|2.7|
|**BARON**|2.5|2.9||2.7|2.9|4.1|4.2|5.0|4.0|
|**CHICHIKOV**|3.0|2.4|2.7||3.2|4.8|5.1|6.0|4.1|
|**NOAKES**|2.8|2.2|2.9|3.2||4.9|4.6|4.8|2.5|
|**MIRA**|4.3|4.5|4.1|4.8|4.9||2.9|2.4|4.7|
|**LUCÍA**|5.2|4.2|4.2|5.1|4.6|2.9||3.0|4.8|
|**TEMI**|4.9|4.8|5.0|6.0|4.8|2.4|3.0||4.4|
|**MAMANI**|3.2|2.7|4.0|4.1|2.5|4.7|4.8|4.4||

## Pairwise distances, table-read cast (min 2.04, mean 3.42)

| |JAX|PIP|BARON|CHICHIKOV|NOAKES|MIRA|LUCÍA|TEMI|MAMANI|
|---|---|---|---|---|---|---|---|---|---|
|**JAX**||3.2|2.5|2.6|2.8|5.5|4.0|2.7|3.2|
|**PIP**|3.2||2.9|2.3|2.1|4.7|3.6|2.5|2.7|
|**BARON**|2.5|2.9||2.0|2.8|3.9|3.4|2.8|4.1|
|**CHICHIKOV**|2.6|2.3|2.0||2.8|5.1|4.4|3.4|3.9|
|**NOAKES**|2.8|2.1|2.8|2.8||5.0|4.1|2.6|2.5|
|**MIRA**|5.5|4.7|3.9|5.1|5.0||3.1|4.5|5.9|
|**LUCÍA**|4.0|3.6|3.4|4.4|4.1|3.1||2.6|4.2|
|**TEMI**|2.7|2.5|2.8|3.4|2.6|4.5|2.6||2.7|
|**MAMANI**|3.2|2.7|4.1|3.9|2.5|5.9|4.2|2.7||

