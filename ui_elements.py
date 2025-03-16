import streamlit as st
from functions import (
    store_in_state,
    get_from_session_state,
    process_uploaded_file,
    analyze_uploaded_sources,
    safe_int
)
from llm_choice import get_llm
from rag_helpers import search_faiss
from prompts import generate_job_ad, generate_interview_guide
from ui_styling import apply_base_styling

def show_progress_bar(current_page, total_pages):
    """
    Called by app.py to show a horizontal progress bar at the top.
    """
    fraction = (current_page + 1) / total_pages
    st.progress(fraction)

#####################################
# SIDEBAR LINKS
#####################################
def show_sidebar_links():
    """
    In the sidebar, we place two special buttons: 
    'About Vacalyser' & 'About the Technology'.
    """
    st.sidebar.write("---")
    if st.sidebar.button("About Vacalyser"):
        from navigation import PAGE_FUNCTIONS, about_vacalyser_page
        idx = PAGE_FUNCTIONS.index(about_vacalyser_page)
        st.session_state["current_section"] = idx
        st.rerun()
    if st.sidebar.button("About the Technology"):
        from navigation import PAGE_FUNCTIONS, about_technology_page
        idx = PAGE_FUNCTIONS.index(about_technology_page)
        st.session_state["current_section"] = idx
        st.rerun()

###########################
# 1) START DISCOVERY PAGE
###########################
def start_discovery_page():
    apply_base_styling()
    show_sidebar_links()

    if "llm_choice" not in st.session_state:
        st.session_state["llm_choice"] = "openai_3.5"

    # Model selection
    st.sidebar.subheader("Model Choice")
    llm_options = ["local_llama", "openai_o3_mini", "openai_3.5"]
    chosen_model = st.sidebar.selectbox(
        "Select LLM:", llm_options, index=llm_options.index(st.session_state["llm_choice"])
    )
    st.session_state["llm_choice"] = chosen_model

    # Temperature
    current_temp = st.session_state.get("model_temperature", 0.2)
    st.session_state["model_temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, current_temp, 0.05)

    # Heading / Intro
    st.image("images/lama.png", width=80)
    st.title("Vacalyser")
    st.markdown("""
    **Enhancing hiring workflows** with intelligent suggestions and automations.  
    By leveraging FAISS for semantic search and LLaMA/OpenAI for generative AI, 
    we help teams fine-tune job postings and CVs efficiently, enabling better hiring outcomes.
    """)

    st.header("🔍 Start Discovery")
    st.write("Enter a Job Title, optionally a link or an uploaded file. We'll auto-fill fields where possible.")

    default_url = get_from_session_state("input_url", "http://www.")
    col1, col2 = st.columns([1,1])
    with col1:
        job_title = st.text_input("Enter a **Job Title**", get_from_session_state("job_title",""))
        store_in_state("job_title", job_title)

        input_url = st.text_input("🔗 Link to a Job Ad / Company Website", value=default_url)
        store_in_state("input_url", input_url)

    with col2:
        uploaded_file = st.file_uploader("Upload Job Ad (PDF, DOCX, TXT)", type=["pdf","docx","txt"])
        if uploaded_file:
            content = process_uploaded_file(uploaded_file)
            store_in_state("uploaded_file", content)

    # Buttons row
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("Analyse Sources"):
            analyze_uploaded_sources()  # merges PDF + URL, auto-fills session state

    with c2:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

#--------------------------------
# 2) COMPANY INFORMATION
#--------------------------------
def company_information_page():
    apply_base_styling()
    show_sidebar_links()

    st.header("🏢 Company Information")

    company_name = st.text_input("Company Name", get_from_session_state("company_name",""))
    store_in_state("company_name", company_name)

    loc_val = get_from_session_state("location","Düsseldorf, Germany")
    location_input = st.text_input("Location", loc_val)
    store_in_state("location", location_input)

    colA, colB = st.columns([1,1])
    with colA:
        place_of_work = st.checkbox("Is this the actual place of work?", value=True)
    with colB:
        fully_remote = st.checkbox("Alternatively 100% remote?", value=False)
    store_in_state("place_of_work_confirmed", place_of_work)
    store_in_state("fully_remote", fully_remote)

    if not place_of_work and not fully_remote:
        alt_work = st.text_input("Please provide the actual address of place of work","")
        store_in_state("alternate_work_address", alt_work)

    web_default = get_from_session_state("company_website","https://www.")
    website = st.text_input("Company Website / Social Media Links", web_default)
    store_in_state("company_website", website)

    if st.button("Scrape Website for Mission & Vision"):
        # placeholder scraping
        found_mission = "(Demo) Discovered mission statement from website scraping."
        store_in_state("company_mission", found_mission)
        st.info("Mission & Vision updated from website scraping (demo).")

    # Industry + Company Size
    top10_inds = [
        "Automotive", "Consulting", "E-Commerce", "Education", "Finance",
        "Healthcare", "Manufacturing", "Retail", "Technology", "Tourism"
    ]
    stored_ind = get_from_session_state("industry","")
    sorted_inds = sorted(top10_inds)
    idx_ind = 0
    if stored_ind in sorted_inds:
        idx_ind = sorted_inds.index(stored_ind)
    chosen_ind = st.selectbox("Industry / Sector", sorted_inds, index=idx_ind)
    store_in_state("industry", chosen_ind)

    size_opts = ["Small (<50)", "Medium (50-500)", "Large (>500)"]
    st_size = get_from_session_state("company_size","Small (<50)")
    if st_size not in size_opts:
        st_size = "Small (<50)"
    chosen_size = st.selectbox("Company Size", size_opts, index=size_opts.index(st_size))
    store_in_state("company_size", chosen_size)

    # Mission & Vision
    mission_txt = st.text_area("Mission & Vision", get_from_session_state("company_mission",""))
    store_in_state("company_mission", mission_txt)

    # Next/Back
    cA, cB = st.columns([1,1])
    with cA:
        if st.button("⬅ Back (Start)"):
            st.session_state["current_section"] -= 1
            st.rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

#-----------------------------------
# 3) DEPARTMENT INFORMATION
#-----------------------------------
def department_information_page():
    apply_base_styling()
    show_sidebar_links()

    st.header("🏢 Department Information")

    dept = st.text_input("Department Name", get_from_session_state("department",""))
    store_in_state("department", dept)

    tm_val = get_from_session_state("team_size",0)
    new_team_size = st.number_input("Team Size in this Department", value=int(tm_val), min_value=0)
    store_in_state("team_size", new_team_size)

    dspv = st.text_input("Direct Supervisor (Full Name)", get_from_session_state("direct_supervisor",""))
    store_in_state("direct_supervisor", dspv)

    dspv_email = st.text_input("Supervisor E-Mail", get_from_session_state("supervisor_email",""))
    store_in_state("supervisor_email", dspv_email)

    dept_strat = st.text_area("Department Strategy / Future Plans", get_from_session_state("department_strategy",""))
    store_in_state("department_strategy", dept_strat)

    dept_challenge = st.text_area("Challenges / Problems within Department/Team",
                                  get_from_session_state("department_challenges",""))
    store_in_state("department_challenges", dept_challenge)

    # Technologies
    st.subheader("Technologies / Software Commonly Used")
    recommended_techs = [
        "Python","Java","JavaScript","React","Angular","SQL","NoSQL","AWS",
        "Azure","Docker","Kubernetes","Salesforce","SAP","Tableau","PowerBI"
    ]
    st.caption("Click any that apply; you can also add your own below.")
    stored_techs = set(get_from_session_state("technologies_used",[]))
    col_techs = st.columns(5)
    for i,tech in enumerate(recommended_techs):
        cidx = i % 5
        if col_techs[cidx].button(tech):
            stored_techs.add(tech)

    manual_tech = st.text_input("Add Another Technology:")
    if st.button("Add Technology"):
        if manual_tech.strip():
            stored_techs.add(manual_tech.strip())

    store_in_state("technologies_used", list(stored_techs))
    if stored_techs:
        st.write("**Currently Selected Technologies:**", ", ".join(stored_techs))

    # Culture / Collaborations
    c_opts = ["Agile","Hierarchical","Cross-functional","Startup Mindset","Other"]
    cur_cult = get_from_session_state("department_culture","Agile")
    if cur_cult not in c_opts:
        cur_cult = "Agile"
    chosen_culture = st.selectbox("Department Culture / Environment", c_opts, index=c_opts.index(cur_cult))
    store_in_state("department_culture", chosen_culture)

    collab_opts = ["Finance","HR","Marketing","IT","Legal","External Vendors"]
    def_collabs = get_from_session_state("department_collaborations",[])
    chosen_collabs = st.multiselect("Key Collaborations with Other Departments", collab_opts, default=def_collabs)
    store_in_state("department_collaborations", chosen_collabs)

    # Next/Back
    cA, cB = st.columns([1,1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

#-----------------------------------
# 4) ROLE DESCRIPTION
#-----------------------------------
def role_description_page():
    apply_base_styling()
    show_sidebar_links()

    st.header("👤 Role Description")

    # Reason for Hiring
    st.write("**Reason for Hiring** (check all that apply):")
    reason_opts = ["New Role","Growth","Replacement","Project-based"]
    current_reason = set(get_from_session_state("job_reason",[]))
    updates = []
    for r in reason_opts:
        checked = r in current_reason
        val = st.checkbox(r, value=checked, key=f"cb_{r}")
        if val:
            updates.append(r)
    store_in_state("job_reason", updates)

    # Responsibilities
    st.subheader("Key Responsibilities / Accountabilities")
    existing_resps = set(get_from_session_state("responsibility_distribution", []))

    if st.button("Get AI-Generated Responsibilities"):
        suggestions = rag_suggestions("responsibilities for role")
        st.info("Click on any suggested responsibility to add it.")
        for item in suggestions:
            if st.button(item):
                existing_resps.add(item)

    new_resp = st.text_input("Add a Responsibility/Accountability:")
    if st.button("Add Responsibility"):
        if new_resp.strip():
            existing_resps.add(new_resp.strip())
    store_in_state("responsibility_distribution", list(existing_resps))

    if existing_resps:
        st.write("**Currently Selected Responsibilities:**", ", ".join(existing_resps))

    # Core Tasks
    st.subheader("Core Tasks or Duties")
    existing_tasks = set(get_from_session_state("tasks", []))

    if st.button("Get AI-Generated Tasks"):
        suggestions = rag_suggestions("tasks for role")
        st.info("Click on any suggested task to add it.")
        for item in suggestions:
            if st.button(item):
                existing_tasks.add(item)

    new_task = st.text_input("Add a Task/Duty:")
    if st.button("Add Task"):
        if new_task.strip():
            existing_tasks.add(new_task.strip())
    store_in_state("tasks", list(existing_tasks))

    if existing_tasks:
        st.write("**Currently Selected Tasks:**", ", ".join(existing_tasks))

    # Challenges
    st.subheader("Typical Challenges in This Role")
    existing_challenges = set(get_from_session_state("job_challenges", []))

    if st.button("Get AI-Generated Challenges"):
        suggestions = rag_suggestions("challenges for role")
        st.info("Click on any suggested challenge to add it.")
        for item in suggestions:
            if st.button(item):
                existing_challenges.add(item)

    new_chal = st.text_input("Add a Challenge:")
    if st.button("Add Challenge"):
        if new_chal.strip():
            existing_challenges.add(new_chal.strip())
    store_in_state("job_challenges", list(existing_challenges))

    if existing_challenges:
        st.write("**Currently Selected Challenges:**", ", ".join(existing_challenges))

    st.markdown("---")
    st.subheader("Travel & Remote Requirements")

    travel_opts = ["None","Occasional","Frequent"]
    cur_travel = get_from_session_state("travel_required_flag","None")
    if cur_travel not in travel_opts:
        cur_travel = "None"
    chosen_travel = st.selectbox("Is Travel Required?", travel_opts, index=travel_opts.index(cur_travel))
    store_in_state("travel_required_flag", chosen_travel)

    if chosen_travel != "None":
        travel_details = st.text_area("Travel Details (frequency, locations, purpose)",
                                      get_from_session_state("travel_required",""))
        store_in_state("travel_required", travel_details)
    else:
        store_in_state("travel_required","")

    remote_opts = ["None (on-site)","Partial (hybrid)","Fully Remote"]
    cur_remote = get_from_session_state("remote_policy","None (on-site)")
    if cur_remote not in remote_opts:
        cur_remote = "None (on-site)"
    chosen_remote = st.selectbox("Remote / Hybrid Work Policy", remote_opts, index=remote_opts.index(cur_remote))
    store_in_state("remote_policy", chosen_remote)

    # Next/Back
    cA, cB = st.columns([1,1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

def rag_suggestions(query_text: str):
    """
    Attempt to retrieve tokens from local FAISS index. 
    We'll do a search for 'query_text', then parse the 'excerpt' field.
    """
    results = search_faiss(query_text, top_k=3)
    tokens = []
    for res in results:
        excerpt = res.get("excerpt","")
        # simplistic splitting
        for t in excerpt.split():
            t = t.strip(",.!?;:-").strip()
            if t:
                tokens.append(t)
    return tokens

#-----------------------------------
# 5) TASK SCOPE (REDESIGNED)
#-----------------------------------
def task_scope_page():
    apply_base_styling()
    show_sidebar_links()

    st.header("🗂️ Task Scope")
    st.markdown("""
    This page shows tasks auto-extracted from your file (if any) or from earlier steps. 
    You can edit them, remove them, or add new ones. 
    Additionally, we can retrieve tasks from FAISS or an LLM if desired.
    """)

    # Show existing tasks from the 'tasks' key
    current_tasks = get_from_session_state("tasks", [])
    updated_tasks = set(current_tasks)  # for mutation

    st.write("**Current Tasks (Auto-Filled or Manually Added):**")
    for t in current_tasks:
        colT1, colT2 = st.columns([4,1])
        with colT1:
            st.write("- ", t)
        with colT2:
            if st.button(f"Remove: {t}"):
                updated_tasks.discard(t)
    store_in_state("tasks", list(updated_tasks))

    # Add new tasks manually
    new_task_val = st.text_input("Add Another Task:")
    if st.button("Add This Task"):
        if new_task_val.strip():
            updated_tasks.add(new_task_val.strip())
            store_in_state("tasks", list(updated_tasks))
            st.rerun()

    st.markdown("---")
    st.subheader("Retrieve Additional Tasks from FAISS / LLM")

    colFa, colLL = st.columns([1,1])
    with colFa:
        st.write("**FAISS Task Search**")
        if st.button("Search local index for relevant tasks"):
            # e.g. "tasks for data engineer"
            job_tit = get_from_session_state("job_title","universal role")
            more_tokens = rag_suggestions(f"tasks for {job_tit}")
            if not more_tokens:
                st.warning("No relevant tasks found in local index.")
            else:
                st.info("Click to add any token/word to tasks.")
                for tok in more_tokens[:50]:
                    if st.button(tok):
                        updated_tasks.add(tok)
                        store_in_state("tasks", list(updated_tasks))
                        st.rerun()

    with colLL:
        st.write("**LLM-based Task Suggestion**")
        if st.button("Get LLM Suggestions for Tasks"):
            # simple approach
            jt = get_from_session_state("job_title","some role")
            prompt = f"List 8 relevant tasks for a {jt}, short bullet form."
            llm = get_llm()
            resp = llm(prompt)
            st.write("**LLM Tasks (raw):**")
            st.write(resp)
            st.info("Copy/paste or manually add above, or parse them further if desired.")

    st.markdown("---")
    st.subheader("Autonomy Level")
    auto_opts = ["Low","Medium","High"]
    c_auto = get_from_session_state("autonomy_level","Medium")
    if c_auto not in auto_opts:
        c_auto = "Medium"
    chosen_auto = st.selectbox("Choose Autonomy Level for These Tasks", auto_opts, index=auto_opts.index(c_auto))
    store_in_state("autonomy_level", chosen_auto)

    # Next/Back
    cA, cB = st.columns([1,1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

#-----------------------------------
# 6) REQUIRED SKILLS & COMPETENCIES
#-----------------------------------
def skills_competencies_page():
    apply_base_styling()
    show_sidebar_links()

    st.header("🛠️ Required Skills & Competencies")
    st.markdown("""
    We can parse skills from local CV data (FAISS) or from LLM suggestions, then 
    assign them to Must-Have or Nice-to-Have categories.  
    **(Simulated drag-and-drop** with add/remove buttons).
    """)

    # Must-Have Hard
    must_hard_raw = set([s.strip() for s in get_from_session_state("must_have_hard","").split(",") if s.strip()])
    # Must-Have Soft
    must_soft_raw = set([s.strip() for s in get_from_session_state("must_have_soft","").split(",") if s.strip()])
    # Nice-Have Hard
    nice_hard_raw = set([s.strip() for s in get_from_session_state("nice_have_hard","").split(",") if s.strip()])
    # Nice-Have Soft
    nice_soft_raw = set([s.strip() for s in get_from_session_state("nice_have_soft","").split(",") if s.strip()])

    colA, colB = st.columns([1,1])
    with colA:
        if st.button("Suggest Skills via LLM"):
            jt = get_from_session_state("job_title","")
            if jt:
                prompt = f"List the top 10 short skills for {jt}: 5 Hard, 5 Soft. Each as one line."
            else:
                prompt = "List the top 10 short skills: 5 Hard, 5 Soft. Each as one line."
            llm = get_llm()
            ans = llm(prompt)
            st.markdown("**LLM Suggestions (raw):**")
            st.write(ans)

    with colB:
        st.write("**Or get Skills from local CV index** (FAISS search).")
        if st.button("Search local index for relevant skill words"):
            job_title = get_from_session_state("job_title","some job")
            tokens = rag_suggestions(f"skills for {job_title}")
            if not tokens:
                st.warning("No skill tokens found from local index.")
            else:
                st.info("Click any to add to Must-Have Hard (default). Then you can move them below.")
                for tok in tokens[:40]:
                    if st.button(tok):
                        must_hard_raw.add(tok)
                        store_in_state("must_have_hard", ", ".join(must_hard_raw))
                        st.rerun()

    st.markdown("---")

    # Must-Have Hard
    st.subheader("Must-Have Hard Skills")
    if must_hard_raw:
        st.caption("Currently assigned Must-Have Hard Skills. Click to remove.")
        for skill in list(must_hard_raw):
            if st.button(f"Remove '{skill}' from Must-Have Hard"):
                must_hard_raw.discard(skill)
                store_in_state("must_have_hard", ", ".join(must_hard_raw))
                st.rerun()

    new_must_hard = st.text_input("Add Hard Skill to Must-Have:")
    if st.button("Add Must-Have Hard"):
        if new_must_hard.strip():
            must_hard_raw.add(new_must_hard.strip())
            store_in_state("must_have_hard", ", ".join(must_hard_raw))
            st.rerun()

    st.markdown("---")
    # Must-Have Soft
    st.subheader("Must-Have Soft Skills")
    if must_soft_raw:
        st.caption("Click any skill to remove it from Must-Have Soft.")
        for skill in list(must_soft_raw):
            if st.button(f"Remove '{skill}' from Must-Have Soft"):
                must_soft_raw.discard(skill)
                store_in_state("must_have_soft", ", ".join(must_soft_raw))
                st.rerun()

    new_must_soft = st.text_input("Add Soft Skill to Must-Have:")
    if st.button("Add Must-Have Soft"):
        if new_must_soft.strip():
            must_soft_raw.add(new_must_soft.strip())
            store_in_state("must_have_soft", ", ".join(must_soft_raw))
            st.rerun()

    st.markdown("---")
    # Nice-to-Have Hard
    st.subheader("Nice-to-Have Hard Skills")
    if nice_hard_raw:
        st.caption("Click any skill to remove it from Nice-to-Have Hard.")
        for skill in list(nice_hard_raw):
            if st.button(f"Remove '{skill}' from Nice-to-Have Hard"):
                nice_hard_raw.discard(skill)
                store_in_state("nice_have_hard", ", ".join(nice_hard_raw))
                st.rerun()

    new_nice_hard = st.text_input("Add Hard Skill to Nice-to-Have:")
    if st.button("Add Nice-to-Have Hard"):
        if new_nice_hard.strip():
            nice_hard_raw.add(new_nice_hard.strip())
            store_in_state("nice_have_hard", ", ".join(nice_hard_raw))
            st.rerun()

    st.markdown("---")
    # Nice-to-Have Soft
    st.subheader("Nice-to-Have Soft Skills")
    if nice_soft_raw:
        st.caption("Click any skill to remove it from Nice-to-Have Soft.")
        for skill in list(nice_soft_raw):
            if st.button(f"Remove '{skill}' from Nice-to-Have Soft"):
                nice_soft_raw.discard(skill)
                store_in_state("nice_have_soft", ", ".join(nice_soft_raw))
                st.rerun()

    new_nice_soft = st.text_input("Add Soft Skill to Nice-to-Have:")
    if st.button("Add Nice-to-Have Soft"):
        if new_nice_soft.strip():
            nice_soft_raw.add(new_nice_soft.strip())
            store_in_state("nice_have_soft", ", ".join(nice_soft_raw))
            st.rerun()

    # Next/Back
    colA, colB = st.columns([1,1])
    with colA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.rerun()
    with colB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

#-----------------------------------
# 7) BENEFITS & COMPENSATION
#-----------------------------------
def benefits_compensation_page():
    apply_base_styling()
    show_sidebar_links()

    st.header("💰 Benefits & Compensation")

    st.subheader("Salary Range")
    c1, c2 = st.columns(2)
    min_sal = get_from_session_state("min_salary", 50000)
    max_sal = get_from_session_state("max_salary", 70000)
    updated_min = c1.number_input("Minimum Salary (€)", value=min_sal, step=1000)
    updated_max = c2.number_input("Maximum Salary (€)", value=max_sal, step=1000)
    store_in_state("min_salary", updated_min)
    store_in_state("max_salary", updated_max)
    store_in_state("salary_range", f"{updated_min}-{updated_max}")

    st.subheader("Key Benefits")
    benefits_list = set(get_from_session_state("benefits", []))
    if st.button("Show Top 10 Benefit Suggestions"):
        tokens = rag_suggestions("top 10 common job benefits")
        for tok in tokens:
            if st.button(tok):
                benefits_list.add(tok)
                store_in_state("benefits", list(benefits_list))
                st.rerun()

    new_ben = st.text_input("Add a Benefit:")
    if st.button("Add Benefit"):
        if new_ben.strip():
            benefits_list.add(new_ben.strip())
            store_in_state("benefits", list(benefits_list))
            st.rerun()
    if benefits_list:
        st.write("**Selected Benefits:**", ", ".join(benefits_list))

    st.subheader("Health Benefits")
    health_list = set(get_from_session_state("health_benefits", []))
    if st.button("Show Health Benefit Suggestions"):
        tokens = rag_suggestions("health benefits")
        for t in tokens:
            if st.button(t):
                health_list.add(t)
                store_in_state("health_benefits", list(health_list))
                st.rerun()

    new_health = st.text_input("Add a Health Benefit:")
    if st.button("Add Health Benefit"):
        if new_health.strip():
            health_list.add(new_health.strip())
            store_in_state("health_benefits", list(health_list))
            st.rerun()
    if health_list:
        st.write("**Selected Health Benefits:**", ", ".join(health_list))

    st.subheader("Learning & Development Opportunities")
    lnd_list = set(get_from_session_state("learning_opportunities", []))
    if st.button("Show L&D Suggestions"):
        tokens = rag_suggestions("learning and development benefits")
        for t in tokens:
            if st.button(t):
                lnd_list.add(t)
                store_in_state("learning_opportunities", list(lnd_list))
                st.rerun()

    new_lnd = st.text_input("Add an L&D Opportunity:")
    if st.button("Add L&D"):
        if new_lnd.strip():
            lnd_list.add(new_lnd.strip())
            store_in_state("learning_opportunities", list(lnd_list))
            st.rerun()
    if lnd_list:
        st.write("**Selected L&D Opportunities:**", ", ".join(lnd_list))

    # Next/Back
    colA, colB = st.columns([1,1])
    with colA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.rerun()
    with colB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

#-----------------------------------
# 8) RECRUITMENT PROCESS PAGE
#-----------------------------------
def recruitment_process_page():
    apply_base_styling()
    show_sidebar_links()

    st.header("🏁 Recruitment Process")

    st.markdown("Define your entire recruitment flow, from initial approvals to final hiring steps.")

    st.subheader("Internal Contacts (Need / Authority / Money)")
    cA, cB, cC = st.columns(3)
    with cA:
        need_name = st.text_input("Name (Need)", get_from_session_state("need_name",""))
        store_in_state("need_name", need_name)
        need_email = st.text_input("E-Mail (Need)", get_from_session_state("need_email",""))
        store_in_state("need_email", need_email)
    with cB:
        auth_name = st.text_input("Name (Authority)", get_from_session_state("authority_name",""))
        store_in_state("authority_name", auth_name)
        auth_email = st.text_input("E-Mail (Authority)", get_from_session_state("authority_email",""))
        store_in_state("authority_email", auth_email)
    with cC:
        money_name = st.text_input("Name (Budget Holder)", get_from_session_state("money_name",""))
        store_in_state("money_name", money_name)
        money_email = st.text_input("E-Mail (Budget Holder)", get_from_session_state("money_email",""))
        store_in_state("money_email", money_email)

    st.subheader("Documents / Requirements")
    doc_text = st.text_area("List of required documents for applying or internal approvals",
                            get_from_session_state("required_documents",""))
    store_in_state("required_documents", doc_text)

    st.subheader("Approvals & Mail Loops")
    approval_text = st.text_area("Who must approve and at which stages?",
                                 get_from_session_state("approval_flow",""))
    store_in_state("approval_flow", approval_text)

    st.subheader("Interview Process & Timeline")
    iv_num = safe_int(get_from_session_state("interview_stages",0))
    updated_iv = st.number_input("Number of Interview Rounds", min_value=0, value=iv_num)
    store_in_state("interview_stages", updated_iv)

    timeline_val = get_from_session_state("application_timeline","")
    updated_timeline = st.text_input("Application / Hiring Timeline", timeline_val)
    store_in_state("application_timeline", updated_timeline)

    # Next/Back
    cA, cB = st.columns([1,1])
    with cA:
        if st.button("⬅ Back"):
            st.session_state["current_section"] -= 1
            st.rerun()
    with cB:
        if st.button("Next ➡"):
            st.session_state["current_section"] += 1
            st.rerun()

#-----------------------------------
# 9) SUMMARY & OUTPUTS PAGE
#-----------------------------------
def summary_outputs_page():
    apply_base_styling()
    show_sidebar_links()
    st.header("📄 Final Summary")

    st.markdown("Review all key fields. You can go back to any step to revise, or generate final outputs below.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("General")
        st.write("**Job Title**:", get_from_session_state("job_title","Not provided"))
        st.write("**Company Name**:", get_from_session_state("company_name",""))
        st.write("**Location**:", get_from_session_state("location",""))
        st.write("**Website**:", get_from_session_state("company_website",""))
        st.write("**Industry**:", get_from_session_state("industry",""))
        st.write("**Department**:", get_from_session_state("department",""))
        st.write("**Team Size**:", get_from_session_state("team_size",0))
        st.write("**Direct Supervisor**:", get_from_session_state("direct_supervisor",""))

        st.subheader("Compensation & Benefits")
        st.write("**Salary Range**:", get_from_session_state("salary_range","Not specified"))
        st.write("**Key Benefits**:", get_from_session_state("benefits",[]))
        st.write("**Health Benefits**:", get_from_session_state("health_benefits",[]))
        st.write("**Learning Opp.**:", get_from_session_state("learning_opportunities",[]))

    with c2:
        st.subheader("Role Description")
        st.write("**Reasons**:", get_from_session_state("job_reason",[]))
        st.write("**Responsibilities**:", get_from_session_state("responsibility_distribution",[]))
        st.write("**Tasks**:", get_from_session_state("tasks",[]))
        st.write("**Challenges**:", get_from_session_state("job_challenges",[]))

        st.subheader("Recruitment Process")
        st.write("**Interview Rounds**:", get_from_session_state("interview_stages",0))
        st.write("**Timeline**:", get_from_session_state("application_timeline",""))

    st.markdown("---")
    st.markdown("### Generate Outputs")
    colGen1, colGen2 = st.columns(2)
    with colGen1:
        if st.button("🎯 Generate Job Ad"):
            job_details = dict(st.session_state)
            job_ad = generate_job_ad(job_details)
            st.subheader("Generated Job Ad")
            st.write(job_ad)

    with colGen2:
        if st.button("📝 Generate Interview Guide"):
            job_details = dict(st.session_state)
            guide = generate_interview_guide(job_details, "HR")
            st.subheader("Interview Preparation Guide")
            st.write(guide)

    st.info("You can always return to previous sections to refine details.")

    # optional navigation
    if st.button("⬅ Back"):
        st.session_state["current_section"] -= 1
        st.rerun()

###########################
# Additional pages
###########################
def about_vacalyser_page():
    apply_base_styling()
    show_sidebar_links()

    st.title("About Vacalyser")
    st.markdown("""
    (Your text about the app, grey areas, candidate quality, etc.)
    """)

    if st.button("⬅ Back to Wizard"):
        from navigation import PAGE_FUNCTIONS
        # Jump to summary or start, whichever you prefer:
        st.session_state["current_section"] = 0  # or summary
        st.rerun()

def about_technology_page():
    apply_base_styling()
    show_sidebar_links()

    st.title("About the Technology")
    st.markdown("""
    (Your text about Streamlit, FAISS, local LLaMA, etc.)
    """)

    if st.button("⬅ Back to Wizard"):
        from navigation import PAGE_FUNCTIONS
        st.session_state["current_section"] = 0
        st.rerun()

###########################
# Additional Info Pages
###########################
def technologies_used_page():
    apply_base_styling()
    show_sidebar_links()
    st.title("Technologies Used")
    st.markdown("""(Detail content here)""")
    if st.button("⬅ Back to Wizard"):
        st.session_state["current_section"] = 0
        st.rerun()

def audience_benefits_page():
    apply_base_styling()
    show_sidebar_links()
    st.title("Audience & Benefits")
    st.markdown("""(Detail content here)""")
    if st.button("⬅ Back to Wizard"):
        st.session_state["current_section"] = 0
        st.rerun()

def why_grey_areas_page():
    apply_base_styling()
    show_sidebar_links()
    st.title("Why Identifying 'Grey Areas' Matters")
    st.markdown("""(Detail content here)""")
    if st.button("⬅ Back to Wizard"):
        st.session_state["current_section"] = 0
        st.rerun()

def gdpr_compliance_page():
    apply_base_styling()
    show_sidebar_links()
    st.title("GDPR Compliance & Security")
    st.markdown("""(Detail content here)""")
    if st.button("⬅ Back to Wizard"):
        st.session_state["current_section"] = 0
        st.rerun()

def informative_texts_page():
    apply_base_styling()
    show_sidebar_links()
    st.title("Informative Text for Each Section/Page")
    st.markdown("""(Detail content here)""")
    if st.button("⬅ Back to Wizard"):
        st.session_state["current_section"] = 0
        st.rerun()

def extended_advantages_page():
    apply_base_styling()
    show_sidebar_links()
    st.title("Extended Advantages of Vacalyser")
    st.markdown("""(Detail content here)""")
    if st.button("⬅ Back to Wizard"):
        st.session_state["current_section"] = 0
        st.rerun()
