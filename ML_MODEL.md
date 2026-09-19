# SentinelL402 — Machine Learning Model

## 1. Overview

SentinelL402 uses a supervised machine learning model to classify network traffic as either:

* `BENIGN`
* `DDoS`

The machine learning component is integrated into the SentinelL402 security-analysis pipeline.

The overall flow is:

```text
Network Flow
     ↓
78 CIC-IDS2017 Features
     ↓
Feature Processing
     ↓
Random Forest Model
     ↓
Prediction
     ↓
BENIGN / DDoS
     ↓
Risk Assessment
     ↓
Security Recommendation
```

---

# 2. Dataset

The model was trained using the CIC-IDS2017 dataset.

CIC-IDS2017 is a network intrusion-detection dataset containing realistic network traffic and different attack categories.

For the initial SentinelL402 model, the training data was focused on:

* BENIGN traffic
* DDoS traffic

The training pipeline selected balanced samples from the available data.

The final training dataset contained:

```text
BENIGN samples: 10,000
DDoS samples:   10,000

Total samples:  20,000
```

This produced a balanced binary classification problem.

---

# 3. Input Features

The model requires exactly:

```text
78 network-flow features
```

These features correspond to the CIC-IDS2017 network-flow representation used by SentinelL402.

The feature vector includes information such as:

* Destination port
* Flow duration
* Forward packet count
* Backward packet count
* Forward packet length
* Backward packet length
* Flow packet rate
* Flow byte rate
* Inter-arrival times
* TCP flags
* Header lengths
* Packet statistics
* Subflow statistics
* Window sizes
* Active time
* Idle time

The complete feature list is:

```text
Destination_Port
Flow_Duration
Total_Fwd_Packets
Total_Backward_Packets
Total_Length_of_Fwd_Packets
Total_Length_of_Bwd_Packets
Fwd_Packet_Length_Max
Fwd_Packet_Length_Min
Fwd_Packet_Length_Mean
Fwd_Packet_Length_Std
Bwd_Packet_Length_Max
Bwd_Packet_Length_Min
Bwd_Packet_Length_Mean
Bwd_Packet_Length_Std
Flow_Bytes/s
Flow_Packets/s
Flow_IAT_Mean
Flow_IAT_Std
Flow_IAT_Max
Flow_IAT_Min
Fwd_IAT_Total
Fwd_IAT_Mean
Fwd_IAT_Std
Fwd_IAT_Max
Fwd_IAT_Min
Bwd_IAT_Total
Bwd_IAT_Mean
Bwd_IAT_Std
Bwd_IAT_Max
Bwd_IAT_Min
Fwd_PSH_Flags
Bwd_PSH_Flags
Fwd_URG_Flags
Bwd_URG_Flags
Fwd_Header_Length
Bwd_Header_Length
Fwd_Packets/s
Bwd_Packets/s
Min_Packet_Length
Max_Packet_Length
Packet_Length_Mean
Packet_Length_Std
Packet_Length_Variance
FIN_Flag_Count
SYN_Flag_Count
RST_Flag_Count
PSH_Flag_Count
ACK_Flag_Count
URG_Flag_Count
CWE_Flag_Count
ECE_Flag_Count
Down/Up_Ratio
Average_Packet_Size
Avg_Fwd_Segment_Size
Avg_Bwd_Segment_Size
Fwd_Header_Length.1
Fwd_Avg_Bytes/Bulk
Fwd_Avg_Packets/Bulk
Fwd_Avg_Bulk_Rate
Bwd_Avg_Bytes/Bulk
Bwd_Avg_Packets/Bulk
Bwd_Avg_Bulk_Rate
Subflow_Fwd_Packets
Subflow_Fwd_Bytes
Subflow_Bwd_Packets
Subflow_Bwd_Bytes
Init_Win_bytes_forward
Init_Win_bytes_backward
act_data_pkt_fwd
min_seg_size_forward
Active_Mean
Active_Std
Active_Max
Active_Min
Idle_Mean
Idle_Std
Idle_Max
Idle_Min
```

The SentinelL402 feature processor validates this feature structure before prediction.

---

# 4. Data Preprocessing

The training pipeline performs several preprocessing operations.

## 4.1 Numeric conversion

Network-flow feature values are converted to numeric values.

Invalid numeric values are handled during preprocessing.

## 4.2 Infinite values

Positive and negative infinity values are converted to missing values.

Conceptually:

```text
+∞ → NaN
-∞ → NaN
```

## 4.3 Missing values

Missing values are replaced with:

```text
0
```

This allows the machine learning model to receive a complete numeric feature vector.

---

# 5. Class Mapping

The trained Random Forest model uses two classes:

```text
0 → BENIGN
1 → DDoS
```

Therefore:

```text
Prediction = 0
        ↓
BENIGN
```

and:

```text
Prediction = 1
        ↓
DDoS
```

---

# 6. Model

SentinelL402 uses a:

```text
Random Forest Classifier
```

The model configuration used during training was:

```text
Algorithm:       Random Forest
Number of trees: 200
Random state:    42
Class weight:    balanced
Parallel jobs:   -1
```

The Random Forest contains multiple decision trees.

Each tree produces a prediction, and the forest combines the individual predictions to produce the final classification.

---

# 7. Why Random Forest?

Random Forest was selected because it is well suited to tabular network-flow data.

Advantages include:

* Good performance on structured data
* Handles nonlinear relationships
* Works well with many features
* Provides class probabilities
* Relatively easy to train
* Fast enough for a prototype security-analysis API
* Does not require a deep neural network for this classification task

The model is therefore used as the primary ML detector in SentinelL402.

---

# 8. Model Artifact

The trained model is stored at:

```text
backend/app/ml/models/random_forest.joblib
```

The model is loaded by the SentinelL402 prediction layer.

The repository ignores the model directory through `.gitignore` because trained model artifacts can be large.

---

# 9. Prediction Pipeline

The prediction pipeline is:

```text
API Request
     ↓
78 Features
     ↓
Feature Validation
     ↓
Feature Ordering
     ↓
Numeric Processing
     ↓
Random Forest
     ↓
Prediction
     ↓
Class Label
     ↓
Probability
     ↓
Security Risk
```

The prediction service returns information similar to:

```json
{
  "prediction": 0,
  "label": "BENIGN",
  "probabilities": [0.955, 0.045],
  "confidence": 0.955
}
```

The exact probabilities depend on the supplied network-flow features.

---

# 10. Confidence

The prediction service also exposes a confidence value.

For a two-class Random Forest prediction, the class probabilities indicate how strongly the model favors each class.

For example:

```text
BENIGN = 0.955
DDoS   = 0.045
```

The predicted class is:

```text
BENIGN
```

with confidence:

```text
0.955
```

---

# 11. Security Risk Mapping

The ML result is converted into a higher-level security assessment.

Current SentinelL402 logic uses:

```text
DDoS
 ↓
HIGH risk
```

and:

```text
BENIGN
 ↓
LOW risk
```

For a DDoS prediction, SentinelL402 recommends investigating the source and applying appropriate traffic filtering or rate-limiting controls.

For a BENIGN prediction, SentinelL402 recommends continued monitoring.

---

# 12. Example Prediction

Example input:

```text
78 network-flow features
```

The Random Forest may produce:

```json
{
  "prediction": 0,
  "label": "BENIGN",
  "probabilities": [1.0, 0.0],
  "confidence": 1.0
}
```

The security-analysis layer then produces:

```text
ML Label: BENIGN
Risk Level: LOW
```

The API response can additionally include:

* explanation
* recommendation
* remaining AI credits

---

# 13. Model Evaluation

The trained model was evaluated on a held-out test set.

The observed evaluation results were:

```text
Accuracy:  0.9995
Precision: 1.0000
Recall:    0.9990
F1 Score:  0.9995
```

The confusion matrix was:

```text
                 Predicted
                 BENIGN   DDoS

Actual BENIGN     2000      0
Actual DDoS          2   1998
```

Therefore:

```text
True Negatives:  2000
False Positives:    0
False Negatives:    2
True Positives:  1998
```

These results indicate very strong performance on the selected evaluation dataset.

However, these results should not be interpreted as proof that the model will perform equally well on unseen real-world traffic.

---

# 14. Real-Data Validation

The trained model was also tested on real CIC-IDS2017 flow data.

The validation sample contained:

```text
101 rows
```

Among the rows with available labels:

```text
99 labeled DDoS flows
```

were predicted as DDoS.

Two rows were unlabeled and were predicted as BENIGN.

Because those two rows did not contain a known ground-truth label, they should not be described as confirmed model misses.

---

# 15. Feature Count Verification

The SentinelL402 system verifies that the model receives exactly:

```text
78 features
```

This is important because the model was trained using a specific feature representation.

If the API receives the wrong number of features, the agent rejects the request.

For example:

```text
Expected: 78
Received: 75
```

results in an invalid-argument response rather than allowing an incorrect prediction.

---

# 16. Integration with SentinelL402

The ML model is not exposed directly to the public client.

Instead, the application uses the following architecture:

```text
Client
  ↓
FastAPI
  ↓
Authentication
  ↓
Agent
  ↓
Security Tool
  ↓
Metering
  ↓
Payment Check
  ↓
ML Detector
  ↓
Security Analysis
  ↓
Response
```

This means that ML analysis is part of the metered AI service.

A client cannot simply bypass the metering layer and directly consume the AI service through the normal API flow.

---

# 17. Integration with HTTP 402

When the user's credits are available:

```text
Request
   ↓
Metering
   ↓
Credit available
   ↓
ML prediction
   ↓
Response
```

When credits are exhausted:

```text
Request
   ↓
Metering
   ↓
0 credits
   ↓
HTTP 402 Payment Required
   ↓
Lightning invoice
   ↓
Payment
   ↓
Payment verification
   ↓
Credits added
   ↓
Retry
   ↓
ML prediction
```

This connects the machine-learning system with the L402 payment architecture.

---

# 18. Integration with the Agent

The SentinelL402 agent can receive a natural-language request such as:

```text
Analyze this network traffic for security threats.
```

The agent performs:

```text
Natural Language Intent
        ↓
Intent Classification
        ↓
Security Intent
        ↓
Tool Selection
        ↓
analyze_network_security
        ↓
78-feature validation
        ↓
Metered Security Analysis
        ↓
Random Forest
```

The agent therefore provides a natural-language interface to the underlying ML detector.

---

# 19. Current Limitations

The current model is a prototype security detector and has several limitations.

### Binary classification

The current model primarily distinguishes:

```text
BENIGN
DDoS
```

It does not yet provide a complete multi-class intrusion-detection system.

### Dataset dependence

The model was trained using CIC-IDS2017 data.

Real-world traffic can differ significantly from training data.

### Dataset shift

Network behavior changes over time.

A model trained on historical traffic may require retraining or monitoring as new traffic patterns appear.

### Limited feature representation

The model depends on the selected 78-feature representation.

Changes to feature extraction can affect prediction quality.

### No automatic blocking

The current system provides analysis and recommendations.

It does not automatically block traffic or modify firewall rules.

---

# 20. Future ML Improvements

Future versions can improve the ML subsystem with:

* Multi-class attack detection
* Additional intrusion datasets
* Real-time traffic ingestion
* Online monitoring
* Model drift detection
* Explainable AI
* SHAP-based explanations
* Anomaly detection
* Ensemble models
* Deep learning models
* LSTM-based sequence detection
* Transformer-based network-flow analysis
* Continuous model evaluation
* Automated retraining pipelines

A future architecture could be:

```text
Network Traffic
      ↓
Flow Extraction
      ↓
Feature Processor
      ↓
┌──────────────────────────┐
│ ML Detection Layer       │
│                          │
│ Random Forest            │
│ LSTM                     │
│ Anomaly Detector         │
│ Transformer              │
└──────────────────────────┘
      ↓
Threat Intelligence
      ↓
Risk Engine
      ↓
SentinelL402 Agent
```

---

# 21. Reproducibility

The important model-training parameters are:

```text
Dataset:        CIC-IDS2017
Classes:        BENIGN / DDoS
Samples:        20,000
Features:       78
Trees:          200
Random state:   42
Class weight:   balanced
Jobs:           -1
```

Keeping these parameters documented makes it possible to reproduce or improve the model in future versions.

---

# 22. Summary

The SentinelL402 machine-learning subsystem currently consists of:

```text
CIC-IDS2017
      ↓
78 Features
      ↓
Preprocessing
      ↓
Random Forest
      ↓
BENIGN / DDoS
      ↓
Risk Assessment
      ↓
Metered AI Service
      ↓
HTTP 402
      ↓
Lightning Payment
      ↓
Retry
```

The current model provides the ML detection component of the SentinelL402 metered AI security platform.

The next major objective is to evolve this prototype into a production-ready security intelligence system with stronger validation, multi-class detection, model monitoring, and advanced sequence-based models.
