import sys
from pathlib import Path

import pandas as pd
import streamlit as st



BASE_DIR = Path(__file__).resolve().parent.parent

SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))



from checker import diagnose_case
from engine import diagnose
from review import create_review
from audit import save_audit_record, load_audit_log



st.set_page_config(
    page_title="NetSage AI",
    page_icon="🌐",
    layout="wide"
)



DATA_PATH = (
    BASE_DIR
    / "data"
    / "cases.csv"
)


@st.cache_data
def load_cases():

    return pd.read_csv(
        DATA_PATH
    )


cases = load_cases()




st.title("🌐 NetSage AI")

st.caption(
    "AI-Assisted Network Troubleshooting "
    "with Human Review"
)

st.divider()




with st.sidebar:

    st.header("Navigation")

    page = st.radio(
        "Module",
        [
            "Troubleshooting",
            "Dashboard",
            "Audit Log"
        ]
    )

    st.divider()

    st.success(
        "Human Review: Enabled"
    )



if page == "Troubleshooting":

    st.header(
        "🔧 Network Troubleshooting"
    )

    selected_case_id = st.selectbox(
        "Select Case",
        cases["case_id"].tolist()
    )

    case_row = cases[
        cases["case_id"] == selected_case_id
    ].iloc[0]

    case = case_row.to_dict()


    
    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Case",
            case["case_id"]
        )

    with col2:

        st.metric(
            "Concept",
            case["concept_tag"]
        )

    with col3:

        st.metric(
            "Severity",
            case["severity"]
        )


    st.divider()


    

    st.subheader("🚨 Symptom")

    st.info(
        case["symptom"]
    )


    

    st.subheader("🗺️ Topology")

    st.write(
        case["topology_note"]
    )


    

    st.subheader(
        "💻 Show Command Output"
    )

    st.code(
        str(case["show_outputs"]),
        language="text"
    )


    

    if st.button(
        "🔍 Run Diagnosis",
        type="primary"
    ):

        with st.spinner(
            "Running deterministic checks and AI diagnosis..."
        ):

            
            rule_result = diagnose_case(
                case
            )

            
            ai_result = diagnose(
                case,
                rule_result
            )


        st.session_state[
            "rule_result"
        ] = rule_result

        st.session_state[
            "ai_result"
        ] = ai_result

        st.session_state[
            "current_case"
        ] = case



    if "rule_result" in st.session_state:

        rule_result = st.session_state[
            "rule_result"
        ]

        st.divider()

        st.subheader(
            "🛡️ Deterministic Checks"
        )

        if rule_result["status"] == "ERRORS_DETECTED":

            st.error(
                f"{rule_result['error_count']} "
                "known issue(s) detected"
            )

            for error in rule_result["errors"]:

                st.write(
                    f"**{error['type']}**"
                )

                st.caption(
                    error["message"]
                )

                st.code(
                    error["evidence"]
                )

        else:

            st.success(
                "No known deterministic errors detected."
            )


    

    if "ai_result" in st.session_state:

        ai_result = st.session_state[
            "ai_result"
        ]

        if not ai_result["success"]:

            st.error(
                "AI diagnosis failed."
            )

            st.code(
                ai_result["error"]
            )

        else:

            diagnosis = ai_result[
                "diagnosis"
            ]

            st.divider()

            st.subheader(
                "🤖 AI Diagnosis"
            )

            st.warning(
                "AI output is advisory and requires "
                "human review."
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "**Likely Root Cause**"
                )

                st.write(
                    diagnosis["root_cause"]
                )

            with col2:

                st.markdown(
                    "**OSI Layer**"
                )

                st.write(
                    diagnosis["osi_layer"]
                )


            st.metric(
                "AI Confidence",
                f"{diagnosis['confidence']:.0%}"
            )


            st.markdown(
                "**Evidence**"
            )

            for evidence in diagnosis[
                "evidence"
            ]:

                st.write(
                    f"• {evidence}"
                )


            st.markdown(
                "**Next Command**"
            )

            st.code(
                diagnosis["next_command"]
            )


            st.markdown(
                "**Suggested Fix Steps**"
            )

            for index, step in enumerate(
                diagnosis["fix_steps"],
                start=1
            ):

                st.write(
                    f"{index}. {step}"
                )


            

            st.divider()

            st.subheader(
                "👤 Human Review"
            )

            st.warning(
                "Review the diagnosis before accepting "
                "any proposed fix."
            )


            decision = st.radio(
                "Decision",
                [
                    "Accepted",
                    "Edited",
                    "Rejected"
                ],
                horizontal=True
            )


            reviewer_notes = st.text_area(
                "Reviewer Notes",
                placeholder=(
                    "Explain why you accepted, "
                    "edited, or rejected the diagnosis."
                )
            )


            edited_root_cause = None

            if decision == "Edited":

                edited_root_cause = st.text_area(
                    "Corrected Root Cause",
                    value=diagnosis[
                        "root_cause"
                    ]
                )


            if st.button(
                "💾 Save Human Review"
            ):

                final_diagnosis = diagnosis.copy()

                if (
                    decision == "Edited"
                    and edited_root_cause
                ):

                    final_diagnosis[
                        "root_cause"
                    ] = edited_root_cause


                review = create_review(
                    case_id=case[
                        "case_id"
                    ],
                    ai_diagnosis=diagnosis,
                    decision=decision,
                    reviewer_notes=reviewer_notes,
                    edited_diagnosis=final_diagnosis
                )


                save_audit_record(
                    review
                )


                st.success(
                    "Human review saved successfully."
                )

                st.session_state.pop(
                    "ai_result",
                    None
                )

                st.session_state.pop(
                    "rule_result",
                    None
                )




elif page == "Dashboard":

    st.header(
        "📊 NetSage AI Dashboard"
    )


    audit = load_audit_log()


    total_cases = len(cases)

    reviewed = len(audit)


    accepted = 0
    edited = 0
    rejected = 0


    if not audit.empty:

        accepted = (
            audit["decision"]
            .eq("Accepted")
            .sum()
        )

        edited = (
            audit["decision"]
            .eq("Edited")
            .sum()
        )

        rejected = (
            audit["decision"]
            .eq("Rejected")
            .sum()
        )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Total Cases",
            total_cases
        )


    with col2:

        st.metric(
            "Reviewed",
            reviewed
        )


    with col3:

        st.metric(
            "AI Accepted",
            accepted
        )


    with col4:

        st.metric(
            "AI Rejected",
            rejected
        )


    st.divider()


    

    st.subheader(
        "Cases by Concept"
    )

    concept_counts = (
        cases[
            "concept_tag"
        ]
        .value_counts()
    )

    st.bar_chart(
        concept_counts
    )


    

    st.subheader(
        "Cases by Severity"
    )

    severity_counts = (
        cases[
            "severity"
        ]
        .value_counts()
    )

    st.bar_chart(
        severity_counts
    )


    

    if reviewed:

        agreement_rate = (
            accepted / reviewed
        )

        st.metric(
            "AI / Human Agreement",
            f"{agreement_rate:.1%}"
        )




elif page == "Audit Log":

    st.header(
        "📝 Responsible AI Audit Log"
    )

    audit = load_audit_log()


    if audit.empty:

        st.info(
            "No human reviews have been recorded yet."
        )

    else:

        st.dataframe(
            audit,
            use_container_width=True
        )