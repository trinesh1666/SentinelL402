const API_BASE = "http://127.0.0.1:8000";

const USER_ID = "l402-402-demo-user";

let currentPaymentId = null;


// ============================================================
// EXACT 78 CIC-IDS2017 FEATURES
// ============================================================

const FEATURES = {
    "Destination_Port": 80.0,
    "Flow_Duration": 1000000.0,
    "Total_Fwd_Packets": 10.0,
    "Total_Backward_Packets": 8.0,
    "Total_Length_of_Fwd_Packets": 5000.0,
    "Total_Length_of_Bwd_Packets": 4000.0,
    "Fwd_Packet_Length_Max": 1000.0,
    "Fwd_Packet_Length_Min": 100.0,
    "Fwd_Packet_Length_Mean": 500.0,
    "Fwd_Packet_Length_Std": 100.0,
    "Bwd_Packet_Length_Max": 1000.0,
    "Bwd_Packet_Length_Min": 100.0,
    "Bwd_Packet_Length_Mean": 500.0,
    "Bwd_Packet_Length_Std": 100.0,
    "Flow_Bytes/s": 9000.0,
    "Flow_Packets/s": 18.0,
    "Flow_IAT_Mean": 50000.0,
    "Flow_IAT_Std": 10000.0,
    "Flow_IAT_Max": 100000.0,
    "Flow_IAT_Min": 1000.0,
    "Fwd_IAT_Total": 500000.0,
    "Fwd_IAT_Mean": 50000.0,
    "Fwd_IAT_Std": 10000.0,
    "Fwd_IAT_Max": 100000.0,
    "Fwd_IAT_Min": 1000.0,
    "Bwd_IAT_Total": 400000.0,
    "Bwd_IAT_Mean": 50000.0,
    "Bwd_IAT_Std": 10000.0,
    "Bwd_IAT_Max": 100000.0,
    "Bwd_IAT_Min": 1000.0,
    "Fwd_PSH_Flags": 0.0,
    "Bwd_PSH_Flags": 0.0,
    "Fwd_URG_Flags": 0.0,
    "Bwd_URG_Flags": 0.0,
    "Fwd_Header_Length": 200.0,
    "Bwd_Header_Length": 160.0,
    "Fwd_Packets/s": 10.0,
    "Bwd_Packets/s": 8.0,
    "Min_Packet_Length": 100.0,
    "Max_Packet_Length": 1000.0,
    "Packet_Length_Mean": 500.0,
    "Packet_Length_Std": 100.0,
    "Packet_Length_Variance": 10000.0,
    "FIN_Flag_Count": 0.0,
    "SYN_Flag_Count": 1.0,
    "RST_Flag_Count": 0.0,
    "PSH_Flag_Count": 0.0,
    "ACK_Flag_Count": 1.0,
    "URG_Flag_Count": 0.0,
    "CWE_Flag_Count": 0.0,
    "ECE_Flag_Count": 0.0,
    "Down/Up_Ratio": 0.8,
    "Average_Packet_Size": 500.0,
    "Avg_Fwd_Segment_Size": 500.0,
    "Avg_Bwd_Segment_Size": 500.0,
    "Fwd_Header_Length.1": 200.0,
    "Fwd_Avg_Bytes/Bulk": 0.0,
    "Fwd_Avg_Packets/Bulk": 0.0,
    "Fwd_Avg_Bulk_Rate": 0.0,
    "Bwd_Avg_Bytes/Bulk": 0.0,
    "Bwd_Avg_Packets/Bulk": 0.0,
    "Bwd_Avg_Bulk_Rate": 0.0,
    "Subflow_Fwd_Packets": 10.0,
    "Subflow_Fwd_Bytes": 5000.0,
    "Subflow_Bwd_Packets": 8.0,
    "Subflow_Bwd_Bytes": 4000.0,
    "Init_Win_bytes_forward": 65535.0,
    "Init_Win_bytes_backward": 65535.0,
    "act_data_pkt_fwd": 10.0,
    "min_seg_size_forward": 20.0,
    "Active_Mean": 10000.0,
    "Active_Std": 1000.0,
    "Active_Max": 20000.0,
    "Active_Min": 1000.0,
    "Idle_Mean": 50000.0,
    "Idle_Std": 5000.0,
    "Idle_Max": 60000.0,
    "Idle_Min": 40000.0
};


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener("DOMContentLoaded", async () => {

    const userElement = document.getElementById("userId");

    if (userElement) {
        userElement.textContent = USER_ID;
    }

    await checkAPI();

    await loadUsage();
});


// ============================================================
// CHECK FASTAPI
// ============================================================

async function checkAPI() {

    const statusText =
        document.getElementById("apiStatus");

    const statusDot =
        document.getElementById("apiStatusDot");

    try {

        const response = await fetch(
            `${API_BASE}/health`
        );

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        const data = await response.json();

        if (statusText) {
            statusText.textContent =
                data.status || "API Online";
        }

        if (statusDot) {
            statusDot.style.background = "green";
        }

    } catch (error) {

        if (statusText) {
            statusText.textContent = "API Offline";
        }

        if (statusDot) {
            statusDot.style.background = "red";
        }

        console.error(
            "API connection error:",
            error
        );
    }
}


// ============================================================
// LOAD ACCOUNT USAGE
// ============================================================

async function loadUsage() {

    try {

        const response = await fetch(
            `${API_BASE}/api/usage/${USER_ID}`
        );

        const data = await response.json();

        if (!response.ok) {

            const errorMessage =
                typeof data.detail === "string"
                    ? data.detail
                    : "Unable to load usage";

            throw new Error(errorMessage);
        }

        const creditsElement =
            document.getElementById("credits");

        const requestsElement =
            document.getElementById("requests");

        if (creditsElement) {
            creditsElement.textContent =
                data.credits_remaining;
        }

        if (requestsElement) {
            requestsElement.textContent =
                data.total_requests;
        }

    } catch (error) {

        console.error(
            "Usage error:",
            error
        );
    }
}


// ============================================================
// SECURITY ANALYSIS
// ============================================================

async function analyzeSecurity() {

    const button =
        document.getElementById("analyzeButton");

    if (button) {
        button.disabled = true;
        button.textContent = "Analyzing...";
    }

    hideElement("resultCard");

    try {

        const payload = {

            source: USER_ID,

            event_type:
                document.getElementById("eventType").value,

            severity:
                document.getElementById("severity").value,

            description:
                document.getElementById("description").value,

            features: FEATURES
        };


        const response = await fetch(
            `${API_BASE}/api/security/analyze`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(payload)
            }
        );


        const data = await response.json();


        // ====================================================
        // HTTP 402 PAYMENT REQUIRED
        // ====================================================

        if (response.status === 402) {

            showPaymentRequired(data);

            return;
        }


        if (!response.ok) {

            const errorMessage =
                typeof data.detail === "string"
                    ? data.detail
                    : "Security analysis failed";

            throw new Error(errorMessage);
        }


        showAnalysisResult(data);

        await loadUsage();

    } catch (error) {

        console.error(
            "Security analysis error:",
            error
        );

        alert(
            "Security analysis error: " +
            error.message
        );

    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "🔎 Analyze Network Traffic";
        }
    }
}


// ============================================================
// DISPLAY 402 PAYMENT CHALLENGE
// ============================================================

function showPaymentRequired(data) {

    const detail =
        data.detail || data;


    currentPaymentId =
        detail.payment_id;


    const paymentIdElement =
        document.getElementById("paymentId");

    const paymentAmountElement =
        document.getElementById("paymentAmount");

    const invoiceElement =
        document.getElementById("invoice");

    const paymentMessageElement =
        document.getElementById("paymentMessage");


    if (paymentIdElement) {

        paymentIdElement.textContent =
            detail.payment_id ?? "-";
    }


    if (paymentAmountElement) {

        paymentAmountElement.textContent =
            detail.amount_sats !== undefined
                ? `${detail.amount_sats} sats`
                : "-";
    }


    if (invoiceElement) {

        invoiceElement.value =
            detail.invoice ||
            "Invoice unavailable";
    }


    if (paymentMessageElement) {

        paymentMessageElement.textContent =
            "Payment required before the AI analysis can continue.";
    }


    showElement("paymentCard");
}


// ============================================================
// VERIFY PAYMENT
// ============================================================

async function verifyPayment() {

    if (!currentPaymentId) {

        alert(
            "No payment is currently pending."
        );

        return;
    }


    const message =
        document.getElementById(
            "paymentMessage"
        );


    if (message) {

        message.textContent =
            "Checking Lightning payment...";
    }


    try {

        const response = await fetch(
            `${API_BASE}/api/payment/verify/${currentPaymentId}`,
            {
                method: "POST"
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            const errorMessage =
                typeof data.detail === "string"
                    ? data.detail
                    : "Payment verification failed";

            throw new Error(errorMessage);
        }


        if (data.status === "paid") {

            if (message) {

                message.textContent =
                    "✅ Payment verified. Credits added. Retrying analysis...";
            }


            await loadUsage();


            // Automatically retry the original
            // security analysis after payment.
            await retrySecurityAnalysis();

        } else {

            if (message) {

                message.textContent =
                    "⏳ Payment is still pending. Pay the invoice and try again.";
            }
        }


    } catch (error) {

        console.error(
            "Payment verification error:",
            error
        );


        if (message) {

            message.textContent =
                "Payment verification error: " +
                error.message;
        }
    }
}


// ============================================================
// RETRY SECURITY ANALYSIS AFTER PAYMENT
// ============================================================

async function retrySecurityAnalysis() {

    const payload = {

        source: USER_ID,

        event_type:
            document.getElementById("eventType").value,

        severity:
            document.getElementById("severity").value,

        description:
            document.getElementById("description").value,

        features: FEATURES
    };


    try {

        const response = await fetch(
            `${API_BASE}/api/security/analyze`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(payload)
            }
        );


        const data =
            await response.json();


        if (response.status === 402) {

            showPaymentRequired(data);

            return;
        }


        if (!response.ok) {

            const errorMessage =
                typeof data.detail === "string"
                    ? data.detail
                    : "Retry analysis failed";

            throw new Error(errorMessage);
        }


        showAnalysisResult(data);


        hideElement("paymentCard");


        currentPaymentId = null;


        await loadUsage();


    } catch (error) {

        console.error(
            "Retry error:",
            error
        );


        const message =
            document.getElementById(
                "paymentMessage"
            );


        if (message) {

            message.textContent =
                "Retry failed: " +
                error.message;
        }
    }
}


// ============================================================
// DISPLAY ANALYSIS RESULT
// ============================================================

function showAnalysisResult(data) {

    const prediction =
        document.getElementById("prediction");

    const mlLabel =
        document.getElementById("mlLabel");

    const confidence =
        document.getElementById("confidence");

    const riskLevel =
        document.getElementById("riskLevel");

    const resultCredits =
        document.getElementById("resultCredits");

    const explanation =
        document.getElementById("explanation");

    const recommendation =
        document.getElementById("recommendation");


    if (prediction) {

        prediction.textContent =
            data.ml_prediction ?? "-";
    }


    if (mlLabel) {

        mlLabel.textContent =
            data.ml_label ?? "-";
    }


    if (confidence) {

        if (
            data.confidence !== null &&
            data.confidence !== undefined
        ) {

            confidence.textContent =
                `${(data.confidence * 100).toFixed(2)}%`;

        } else {

            confidence.textContent =
                "N/A";
        }
    }


    if (riskLevel) {

        riskLevel.textContent =
            data.risk_level ?? "-";
    }


    if (resultCredits) {

        resultCredits.textContent =
            data.credits_remaining ?? "-";
    }


    if (explanation) {

        explanation.textContent =
            data.explanation ?? "-";
    }


    if (recommendation) {

        recommendation.textContent =
            data.recommendation ?? "-";
    }


    showElement("resultCard");
}


// ============================================================
// UI HELPERS
// ============================================================

function showElement(id) {

    const element =
        document.getElementById(id);

    if (element) {

        element.classList.remove(
            "hidden"
        );
    }
}


function hideElement(id) {

    const element =
        document.getElementById(id);

    if (element) {

        element.classList.add(
            "hidden"
        );
    }
}
