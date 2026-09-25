/* =========================================================
   SENTINELL402 FRONTEND APPLICATION
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE = "http://127.0.0.1:8001";

const USER_ID = "l402-402-demo-user";

const API_KEY_STORAGE_KEY =
    "sentinell402_api_key";


let currentPaymentId = null;

let paymentSource = null;


/* =========================================================
   CIC-IDS2017 - COMPLETE 78 FEATURES
========================================================= */
 
/* =========================================================
   CIC-IDS2017 - COMPLETE 78 FEATURES
========================================================= */

const FEATURES = {

    "Destination_Port": 80,

    "Flow_Duration": 1000,

    "Total_Fwd_Packets": 10,

    "Total_Backward_Packets": 8,

    "Total_Length_of_Fwd_Packets": 5000,

    "Total_Length_of_Bwd_Packets": 4000,

    "Fwd_Packet_Length_Max": 1500,

    "Fwd_Packet_Length_Min": 40,

    "Fwd_Packet_Length_Mean": 500,

    "Fwd_Packet_Length_Std": 150,

    "Bwd_Packet_Length_Max": 1400,

    "Bwd_Packet_Length_Min": 40,

    "Bwd_Packet_Length_Mean": 500,

    "Bwd_Packet_Length_Std": 120,

    "Flow_Bytes/s": 9000,

    "Flow_Packets/s": 18,

    "Flow_IAT_Mean": 55,

    "Flow_IAT_Std": 20,

    "Flow_IAT_Max": 120,

    "Flow_IAT_Min": 5,

    "Fwd_IAT_Total": 500,

    "Fwd_IAT_Mean": 55,

    "Fwd_IAT_Std": 20,

    "Fwd_IAT_Max": 100,

    "Fwd_IAT_Min": 5,

    "Bwd_IAT_Total": 450,

    "Bwd_IAT_Mean": 56,

    "Bwd_IAT_Std": 18,

    "Bwd_IAT_Max": 110,

    "Bwd_IAT_Min": 6,

    "Fwd_PSH_Flags": 1,

    "Bwd_PSH_Flags": 1,

    "Fwd_URG_Flags": 0,

    "Bwd_URG_Flags": 0,

    "Fwd_Header_Length": 320,

    "Bwd_Header_Length": 256,

    "Fwd_Packets/s": 10,

    "Bwd_Packets/s": 8,

    "Min_Packet_Length": 40,

    "Max_Packet_Length": 1500,

    "Packet_Length_Mean": 500,

    "Packet_Length_Std": 160,

    "Packet_Length_Variance": 25600,

    "FIN_Flag_Count": 0,

    "SYN_Flag_Count": 1,

    "RST_Flag_Count": 0,

    "PSH_Flag_Count": 2,

    "ACK_Flag_Count": 10,

    "URG_Flag_Count": 0,

    "CWE_Flag_Count": 0,

    "ECE_Flag_Count": 0,

    "Down/Up_Ratio": 0.8,

    "Average_Packet_Size": 500,

    "Avg_Fwd_Segment_Size": 500,

    "Avg_Bwd_Segment_Size": 500,

    "Fwd_Header_Length.1": 320,

    "Fwd_Avg_Bytes/Bulk": 0,

    "Fwd_Avg_Packets/Bulk": 0,

    "Fwd_Avg_Bulk_Rate": 0,

    "Bwd_Avg_Bytes/Bulk": 0,

    "Bwd_Avg_Packets/Bulk": 0,

    "Bwd_Avg_Bulk_Rate": 0,

    "Subflow_Fwd_Packets": 10,

    "Subflow_Fwd_Bytes": 5000,

    "Subflow_Bwd_Packets": 8,

    "Subflow_Bwd_Bytes": 4000,

    "Init_Win_bytes_forward": 8192,

    "Init_Win_bytes_backward": 8192,

    "act_data_pkt_fwd": 8,

    "min_seg_size_forward": 20,

    "Active_Mean": 100,

    "Active_Std": 20,

    "Active_Max": 150,

    "Active_Min": 50,

    "Idle_Mean": 1000,

    "Idle_Std": 100,

    "Idle_Max": 1200,

    "Idle_Min": 800

};


/* =========================================================
   VERIFY FEATURE COUNT
========================================================= */

console.log(
    "SentinelL402 feature count:",
    Object.keys(FEATURES).length
);


/* =========================================================
   API KEY MANAGEMENT
========================================================= */

function getAPIKey() {

    return localStorage.getItem(
        API_KEY_STORAGE_KEY
    );
}


function setAPIKey(apiKey) {

    if (!apiKey) {
        return;
    }

    localStorage.setItem(
        API_KEY_STORAGE_KEY,
        apiKey.trim()
    );
}


function clearAPIKey() {

    localStorage.removeItem(
        API_KEY_STORAGE_KEY
    );
}


function getAuthHeaders() {

    const apiKey = getAPIKey();

    const headers = {
        "Content-Type": "application/json"
    };

    if (apiKey) {

        headers["X-API-Key"] =
            apiKey;
    }

    return headers;
}


/* =========================================================
   DOM READY
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const userIdElement =
            document.getElementById(
                "userId"
            );

        if (userIdElement) {

            userIdElement.textContent =
                USER_ID;
        }


        const usageUser =
            document.getElementById(
                "usageUser"
            );

        if (usageUser) {

            usageUser.textContent =
                USER_ID;
        }


        const savedKey =
            getAPIKey();

        const apiKeyStatus =
            document.getElementById(
                "apiKeyStatus"
            );

        if (savedKey && apiKeyStatus) {

            apiKeyStatus.textContent =
                "API key configured.";
        }


        checkAPI();

        loadUsage();

        updateDashboard();


        setInterval(
            () => {

                checkAPI();

                loadUsage();

            },
            15000
        );

    }
);


/* =========================================================
   SECTION NAVIGATION
========================================================= */

function showSection(
    sectionName
) {

    const sections =
        document.querySelectorAll(
            ".dashboard-section"
        );


    sections.forEach(
        section => {

            section.classList.remove(
                "active-section"
            );

        }
    );


    const selectedSection =
        document.getElementById(
            sectionName
        );


    if (selectedSection) {

        selectedSection.classList.add(
            "active-section"
        );
    }


    const navItems =
        document.querySelectorAll(
            ".nav-item"
        );


    navItems.forEach(
        item => {

            item.classList.remove(
                "active"
            );

            if (
                item.dataset.section ===
                sectionName
            ) {

                item.classList.add(
                    "active"
                );
            }

        }
    );


    const pageTitle =
        document.getElementById(
            "pageTitle"
        );

    const pageSubtitle =
        document.getElementById(
            "pageSubtitle"
        );


    const pageInformation = {

        dashboard: [
            "Dashboard",
            "SentinelL402 security and AI monitoring console"
        ],

        security: [
            "Security Analysis",
            "Analyze network traffic using the ML security engine"
        ],

        agent: [
            "AI Agent",
            "Intent routing, tool selection and security analysis"
        ],

        payments: [
            "Payments",
            "Bitcoin Lightning payment and credit information"
        ],

        usage: [
            "Usage",
            "Account-level API usage and credit information"
        ],

        "api-keys": [
            "API Keys",
            "Authentication and API access information"
        ],

        settings: [
            "Settings",
            "Configure SentinelL402 frontend authentication"
        ]

    };


    const information =
        pageInformation[
            sectionName
        ];


    if (information) {

        pageTitle.textContent =
            information[0];

        pageSubtitle.textContent =
            information[1];
    }

}


/* =========================================================
   API HEALTH
========================================================= */

async function checkAPI() {

    try {

        const response =
            await fetch(
                `${API_BASE}/health`,
                {
                    method: "GET",
                    headers: getAuthHeaders()
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        setAPIStatus(
            true,
            data.status || "healthy"
        );


        const dashboardStatus =
            document.getElementById(
                "dashboardApiStatus"
            );


        if (dashboardStatus) {

            dashboardStatus.textContent =
                "Online";
        }


        return data;

    } catch (error) {

        console.error(
            "API health check failed:",
            error
        );


        setAPIStatus(
            false,
            "Offline"
        );


        const dashboardStatus =
            document.getElementById(
                "dashboardApiStatus"
            );


        if (dashboardStatus) {

            dashboardStatus.textContent =
                "Offline";
        }

        return null;
    }
}


/* =========================================================
   API STATUS UI
========================================================= */

function setAPIStatus(
    online,
    message
) {

    const sidebarDot =
        document.getElementById(
            "sidebarStatusDot"
        );

    const sidebarStatus =
        document.getElementById(
            "sidebarStatus"
        );

    const apiDot =
        document.getElementById(
            "apiStatusDot"
        );

    const apiStatus =
        document.getElementById(
            "apiStatus"
        );


    if (sidebarDot) {

        sidebarDot.className =
            `status-dot ${
                online
                    ? "online"
                    : "offline"
            }`;
    }


    if (apiDot) {

        apiDot.className =
            `status-dot ${
                online
                    ? "online"
                    : "offline"
            }`;
    }


    if (sidebarStatus) {

        sidebarStatus.textContent =
            online
                ? "API Online"
                : "API Offline";
    }


    if (apiStatus) {

        apiStatus.textContent =
            message;
    }

}


/* =========================================================
   LOAD USAGE
========================================================= */

async function loadUsage() {
    const userId = "l402-402-demo-user";

    if (!userId) {
        console.warn("No user ID configured.");
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE}/api/usage/${encodeURIComponent(userId)}`,
            {
                method: "GET",
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            console.error(
                `Usage request failed: ${response.status}`
            );
            return;
        }

        const data = await response.json();

        console.log("Usage response:", data);

        // Usage section
        const usageUser = document.getElementById("usageUser");
        const usageCredits = document.getElementById("usageCredits");
        const usageRequests = document.getElementById("usageRequests");

        if (usageUser) {
            usageUser.textContent = data.user_id ?? userId;
        }

        if (usageCredits) {
            usageCredits.textContent =
                data.credits_remaining ?? 0;
        }

        if (usageRequests) {
            usageRequests.textContent =
                data.total_requests ?? 0;
        }

        // Dashboard section
        const dashboardCredits =
            document.getElementById("dashboardCredits");

        const dashboardRequests =
            document.getElementById("dashboardRequests");

        if (dashboardCredits) {
            dashboardCredits.textContent =
                data.credits_remaining ?? 0;
        }

        if (dashboardRequests) {
            dashboardRequests.textContent =
                data.total_requests ?? 0;
        }

    } catch (error) {
        console.error(
            "Failed to load usage:",
            error
        );
    }
}


/* =========================================================
   UPDATE USAGE UI
========================================================= */

function updateUsageUI(
    data,
    errorMessage
) {

    if (!data) {

        const elements = [
            "dashboardCredits",
            "dashboardRequests",
            "credits",
            "requests",
            "usageCredits",
            "usageRequests"
        ];


        elements.forEach(
            id => {

                const element =
                    document.getElementById(
                        id
                    );

                if (element) {

                    element.textContent =
                        "--";
                }

            }
        );


        return;
    }


    const credits =
        data.credits ??
        data.remaining_credits ??
        data.credit_balance ??
        0;


    const requests =
        data.requests ??
        data.total_requests ??
        data.request_count ??
        0;


    const user =
        data.user_id ??
        USER_ID;


    setText(
        "dashboardCredits",
        credits
    );

    setText(
        "dashboardRequests",
        requests
    );

    setText(
        "credits",
        credits
    );

    setText(
        "requests",
        requests
    );

    setText(
        "usageUser",
        user
    );

    setText(
        "usageCredits",
        credits
    );

    setText(
        "usageRequests",
        requests
    );

}


/* =========================================================
   DASHBOARD
========================================================= */

function updateDashboard() {

    loadUsage();

}


/* =========================================================
   SECURITY ANALYSIS
========================================================= */

async function analyzeSecurity() {

    const button =
        document.getElementById(
            "analyzeButton"
        );


    const status =
        document.getElementById(
            "securityStatus"
        );


    const eventType =
        document.getElementById(
            "eventType"
        ).value.trim();


    const severity =
        document.getElementById(
            "severity"
        ).value;


    const description =
        document.getElementById(
            "description"
        ).value.trim();


    if (!eventType || !description) {

        setStatus(
            status,
            "Please fill in all required fields.",
            "error"
        );

        return;
    }


    button.disabled = true;

    setStatus(
        status,
        "Analyzing network traffic...",
        ""
    );


    hideElement(
        "resultCard"
    );

    hideElement(
        "paymentCard"
    );


    const payload = {

        source: "CIC-IDS2017",

        event_type:
            eventType,

        severity:
            severity,

        description:
            description,

        features:
            FEATURES

    };


    try {

        const response =
            await fetch(
                `${API_BASE}/api/security/analyze`,
                {
                    method: "POST",

                    headers:
                        getAuthHeaders(),

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        const data =
            await response.json();


        if (response.status === 402) {

            showPaymentRequired(
                data
            );

            setStatus(
                status,
                "Payment required.",
                "warning"
            );

            return;
        }


        if (response.status === 401) {

            setStatus(
                status,
                "Missing API key. Configure it in Settings.",
                "error"
            );

            return;
        }


        if (response.status === 403) {

            setStatus(
                status,
                "Invalid or unauthorized API key.",
                "error"
            );

            return;
        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `HTTP ${response.status}`
            );
        }


        showAnalysisResult(
            data
        );


        setStatus(
            status,
            "Analysis completed successfully.",
            "success"
        );


        await loadUsage();


    } catch (error) {

        console.error(
            "Security analysis failed:",
            error
        );


        setStatus(
            status,
            error.message ||
            "Security analysis failed.",
            "error"
        );

    } finally {

        button.disabled = false;
    }

}


/* =========================================================
   SECURITY RESULT
========================================================= */

function showAnalysisResult(
    data
) {

    showElement(
        "resultCard"
    );


    const result =
        data.result ||
        data;


    setText(
        "resultSource",
        result.source
    );

    setText(
        "resultEventType",
        result.event_type
    );

    setText(
        "prediction",
        result.ml_prediction
    );

    setText(
        "mlLabel",
        result.ml_label
    );

    setText(
        "confidence",
        formatConfidence(
            result.confidence
        )
    );

    setText(
        "riskLevel",
        result.risk_level
    );

    setText(
        "resultCredits",
        result.credits_remaining
    );

    setText(
        "explanation",
        result.explanation
    );

    setText(
        "recommendation",
        result.recommendation
    );

    setText(
        "llmAnalysis",
        result.llm_analysis
    );


    updatePaymentInformation(
        result
    );
}


/* =========================================================
   SECURITY 402 PAYMENT
========================================================= */

function showPaymentRequired(
    data
) {

    showElement(
        "paymentCard"
    );


    const detail =
        data.detail ||
        data;


    const message =
        detail.message ||
        detail.detail ||
        "Payment required to continue.";


    const invoice =
        detail.invoice ||
        detail.payment_request ||
        "";


    currentPaymentId =
        detail.payment_id ||
        null;


    paymentSource =
        "security";


    setText(
        "paymentMessage",
        message
    );


    setText(
        "paymentAmount",
        detail.amount_sats
            ? `${detail.amount_sats} sats`
            : "--"
    );


    setText(
        "paymentId",
        currentPaymentId || "--"
    );


    const invoiceElement =
        document.getElementById(
            "invoice"
        );


    if (invoiceElement) {

        invoiceElement.value =
            invoice;
    }


    updatePaymentMessage(
        message
    );
}


/* =========================================================
   VERIFY SECURITY PAYMENT
========================================================= */

async function verifyPayment() {

    if (!currentPaymentId) {

        updatePaymentMessage(
            "No payment ID is available."
        );

        return;
    }


    const button =
        document.getElementById(
            "verifyPaymentButton"
        );


    button.disabled = true;


    updatePaymentMessage(
        "Checking Lightning payment..."
    );


    try {

        const response =
            await fetch(
                `${API_BASE}/api/payment/verify/${currentPaymentId}`,
                {
                    method: "POST",
                    headers:
                        getAuthHeaders()
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Payment verification failed: HTTP ${response.status}`
            );
        }


        updatePaymentMessage(
            "Payment verified successfully. Credits restored."
        );


        hideElement(
            "paymentCard"
        );


        await loadUsage();


        setTimeout(
            () => {

                retrySecurityAnalysis();

            },
            500
        );


    } catch (error) {

        console.error(
            error
        );


        updatePaymentMessage(
            error.message ||
            "Payment verification failed."
        );

    } finally {

        button.disabled = false;
    }
}


/* =========================================================
   RETRY SECURITY ANALYSIS
========================================================= */

async function retrySecurityAnalysis() {

    hideElement(
        "paymentCard"
    );

    await analyzeSecurity();

}


/* =========================================================
   AGENT
========================================================= */

async function runAgent() {

    const button =
        document.getElementById(
            "agentRunButton"
        );


    const status =
        document.getElementById(
            "agentStatus"
        );


    const intent =
        document.getElementById(
            "agentIntent"
        ).value;


    const eventType =
        document.getElementById(
            "agentEventType"
        ).value.trim();


    const severity =
        document.getElementById(
            "agentSeverity"
        ).value;


    const description =
        document.getElementById(
            "agentDescription"
        ).value.trim();


    if (!eventType || !description) {

        setStatus(
            status,
            "Please fill in all required fields.",
            "error"
        );

        return;
    }


    button.disabled = true;


    setStatus(
        status,
        "AI Agent is processing the request...",
        ""
    );


    hideElement(
        "agentResultCard"
    );

    hideElement(
        "agentPaymentCard"
    );


    const payload = {

        user_id:
            USER_ID,

        intent:
            intent,

        parameters: {

            source:
                "CIC-IDS2017",

            event_type:
                eventType,

            severity:
                severity,

            description:
                description,

            features:
                FEATURES

        }

    };


    try {

        const response =
            await fetch(
                `${API_BASE}/api/agent/run`,
                {
                    method: "POST",

                    headers:
                        getAuthHeaders(),

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        const data =
            await response.json();


        if (response.status === 402) {

            showAgentPaymentRequired(
                data
            );

            setStatus(
                status,
                "Agent requires payment.",
                "warning"
            );

            return;
        }


        if (response.status === 401) {

            setStatus(
                status,
                "Missing API key. Configure it in Settings.",
                "error"
            );

            return;
        }


        if (response.status === 403) {

            setStatus(
                status,
                "Invalid or unauthorized API key.",
                "error"
            );

            return;
        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `HTTP ${response.status}`
            );
        }


        showAgentResult(
            data
        );


        setStatus(
            status,
            "Agent completed successfully.",
            "success"
        );


        await loadUsage();


    } catch (error) {

        console.error(
            "Agent request failed:",
            error
        );


        setStatus(
            status,
            error.message ||
            "Agent request failed.",
            "error"
        );

    } finally {

        button.disabled = false;
    }

}


/* =========================================================
   AGENT RESULT
========================================================= */

function showAgentResult(
    data
) {

    showElement(
        "agentResultCard"
    );


    const result =
        data.result ||
        data;


    setText(
        "agentAction",
        data.action ||
        result.action
    );


    setText(
        "agentTool",
        data.tool ||
        result.tool
    );


    setText(
        "agentResultSource",
        result.source
    );


    setText(
        "agentResultEventType",
        result.event_type
    );


    setText(
        "agentPrediction",
        result.ml_prediction
    );


    setText(
        "agentMLLabel",
        result.ml_label
    );


    setText(
        "agentConfidence",
        formatConfidence(
            result.confidence
        )
    );


    setText(
        "agentRiskLevel",
        result.risk_level
    );


    setText(
        "agentCredits",
        result.credits_remaining
    );


    setText(
        "agentExplanation",
        result.explanation
    );


    setText(
        "agentRecommendation",
        result.recommendation
    );


    setText(
        "agentLLMAnalysis",
        result.llm_analysis
    );


    setText(
        "agentUserId",
        USER_ID
    );


    setText(
        "agentFeatureCount",
        Object.keys(
            FEATURES
        ).length
    );


    updatePaymentInformation(
        result
    );
}


/* =========================================================
   AGENT PAYMENT
========================================================= */

function showAgentPaymentRequired(
    data
) {

    showElement(
        "agentPaymentCard"
    );


    const detail =
        data.detail ||
        data;


    const message =
        detail.message ||
        detail.detail ||
        "Payment required to continue.";


    const invoice =
        detail.invoice ||
        detail.payment_request ||
        "";


    currentPaymentId =
        detail.payment_id ||
        null;


    paymentSource =
        "agent";


    setText(
        "agentPaymentMessage",
        message
    );


    const invoiceElement =
        document.getElementById(
            "agentInvoice"
        );


    if (invoiceElement) {

        invoiceElement.value =
            invoice;
    }


    setText(
        "paymentId",
        currentPaymentId || "--"
    );


    setText(
        "paymentAmount",
        detail.amount_sats
            ? `${detail.amount_sats} sats`
            : "--"
    );


    updatePaymentMessage(
        message
    );
}


/* =========================================================
   VERIFY AGENT PAYMENT
========================================================= */

async function verifyAgentPayment() {

    if (!currentPaymentId) {

        setStatus(
            document.getElementById(
                "agentStatus"
            ),
            "No payment ID is available.",
            "error"
        );

        return;
    }


    try {

        const response =
            await fetch(
                `${API_BASE}/api/payment/verify/${currentPaymentId}`,
                {
                    method: "POST",
                    headers:
                        getAuthHeaders()
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Payment verification failed: HTTP ${response.status}`
            );
        }


        hideElement(
            "agentPaymentCard"
        );


        await loadUsage();


        setTimeout(
            () => {

                retryAgent();

            },
            500
        );


    } catch (error) {

        console.error(
            error
        );


        setStatus(
            document.getElementById(
                "agentStatus"
            ),
            error.message ||
            "Payment verification failed.",
            "error"
        );
    }
}


/* =========================================================
   RETRY AGENT
========================================================= */

async function retryAgent() {

    hideElement(
        "agentPaymentCard"
    );

    await runAgent();

}


/* =========================================================
   PAYMENT INFORMATION
========================================================= */

function updatePaymentInformation(
    result
) {

    if (!result) {
        return;
    }


    if (
        result.payment_id
    ) {

        currentPaymentId =
            result.payment_id;

        setText(
            "paymentId",
            result.payment_id
        );
    }


    if (
        result.amount_sats
    ) {

        setText(
            "paymentAmount",
            `${result.amount_sats} sats`
        );
    }
}


/* =========================================================
   PAYMENT MESSAGE
========================================================= */

function updatePaymentMessage(
    message
) {

    const element =
        document.getElementById(
            "paymentMessage"
        );


    if (element) {

        element.textContent =
            message;
    }
}


/* =========================================================
   API KEY SAVE
========================================================= */

function saveAPIKey() {

    const input =
        document.getElementById(
            "apiKeyInput"
        );


    const status =
        document.getElementById(
            "apiKeyStatus"
        );


    if (!input) {
        return;
    }


    const apiKey =
        input.value.trim();


    if (!apiKey) {

        setStatus(
            status,
            "Enter an API key.",
            "error"
        );

        return;
    }


    if (
        !apiKey.startsWith(
            "sk_sentinel_"
        )
    ) {

        setStatus(
            status,
            "The API key should start with sk_sentinel_.",
            "warning"
        );

        return;
    }


    setAPIKey(
        apiKey
    );


    input.value = "";


    setStatus(
        status,
        "API key saved.",
        "success"
    );


    checkAPI();

    loadUsage();

}


/* =========================================================
   REMOVE API KEY
========================================================= */

function removeAPIKey() {

    clearAPIKey();


    const status =
        document.getElementById(
            "apiKeyStatus"
        );


    setStatus(
        status,
        "API key removed.",
        "warning"
    );


    loadUsage();

}


/* =========================================================
   HELPERS
========================================================= */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );


    if (!element) {
        return;
    }


    if (
        value === undefined ||
        value === null
    ) {

        element.textContent =
            "--";

        return;
    }


    element.textContent =
        String(value);
}


function setStatus(
    element,
    message,
    type
) {

    if (!element) {
        return;
    }


    element.textContent =
        message;


    element.className =
        "status-text";


    if (type) {

        element.classList.add(
            type
        );
    }
}


function showElement(
    id
) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.style.display =
            "block";
    }
}


function hideElement(
    id
) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.style.display =
            "none";
    }
}


function formatConfidence(
    value
) {

    if (
        value === undefined ||
        value === null
    ) {

        return "--";
    }


    const number =
        Number(value);


    if (
        Number.isNaN(number)
    ) {

        return String(value);
    }


    return `${(
        number * 100
    ).toFixed(2)}%`;
}


/* =========================================================
   DEBUG INFORMATION
========================================================= */

console.log(
    "SentinelL402 frontend loaded."
);

console.log(
    "API:",
    API_BASE
);

console.log(
    "User:",
    USER_ID
);

console.log(
    "Features:",
    Object.keys(
        FEATURES
    ).length
);