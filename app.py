import streamlit as st
import pandas as pd
from MyTasks import TodoManager
from datetime import datetime

st.set_page_config(page_title="Task Master Pro", page_icon='📝', layout="wide")

@st.cache_resource
def get_manager():
    return TodoManager()

manager = get_manager()

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Task Management Dashboard")

with st.sidebar:
    st.header("📂 List Management")
    

    with st.expander("➕ Create New List"):
        new_list_name = st.text_input("List Name", key="new_list_input")
        if st.button("Create List"):
            if new_list_name:
                success, msg = manager.create_list(new_list_name)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a name.")

    # بخش حذف لیست
    st.divider()
    st.subheader("🗑️ Delete a List")
    all_lists = manager.get_all_lists() 
    if all_lists:
        list_to_delete = st.selectbox("Select list to delete", 
                                     options=[l['name'] for l in all_lists],
                                     key="del_list_select")

        list_id_to_del = next(l['id'] for l in all_lists if l['name'] == list_to_delete)
        
        if st.button("Confirm Delete", type="primary"):
            success, msg = manager.delete_list(list_id_to_del)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    else:
        st.info("No lists available.")

tab1, tab2, tab3 = st.tabs(["📋 All Tasks", "➕ Add Task", "📊 Reports"])

with tab1:
    st.subheader("All Tasks Overview")
    tasks = manager.get_tasks_with_list_names()
    
    if not tasks:
        st.info("No tasks found in any list. Start by adding a task!")
    else:
        df = pd.DataFrame(tasks)
    
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            task_to_toggle = st.selectbox("Select Task to Toggle Status", 
                                         options=df['id'].tolist(),
                                         format_func=lambda x: df[df['id']==x]['task_content'].values[0])
            if st.button("Toggle Done/Undone"):

                current_status = df[df['id']==task_to_toggle]['is_done'].values[0]
                new_status = 1 if current_status == 0 else 0
                success, msg = manager.toggle_task_status(task_to_toggle, new_status)
                if success:
                    st.rerun()
                else:
                    st.error(msg)

        with col2:
            task_to_del = st.selectbox("Select Task to Delete", 
                                      options=df['id'].tolist(),
                                      format_func=lambda x: df[df['id']==x]['task_content'].values[0])
            if st.button("Delete Task", type="primary"):
                success, msg = manager.delete_task(task_to_del)
                if success:
                    st.rerun()
                else:
                    st.error(msg)


with tab2:
    st.subheader("Add a New Task to a List")
    all_lists = manager.get_all_lists()
    
    if not all_lists:
        st.error("❌ You must create a list first via the sidebar!")
    else:
        with st.form("task_entry_form"):
            task_text = st.text_input("Task Description")
            list_options = {l['name']: l['id'] for l in all_lists}
            selected_list_name = st.selectbox("Target List", list(list_options.keys()))
            selected_list_id = list_options[selected_list_name]
            
            priority = st.select_slider("Priority", options=[1, 2, 3], value=2, 
                                       format_func=lambda x: ["Low", "Medium", "High"][x-1])
            due_hour = st.number_input("Due Hour (0-23)", 0, 23, 12)
            
            submit_task = st.form_submit_button("Save Task")
            
            if submit_task:
                if task_text:

                    success, msg = manager.add_task(selected_list_id, task_text, priority, due_hour, 0)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Task description cannot be empty.")


with tab3:
    st.subheader("📊 Data Analytics & Reports")
    
    tasks = manager.get_tasks_with_list_names()
    
    if not tasks:
        st.info("Not enough data to generate reports.")
    else:
        df_reports = pd.DataFrame(tasks)
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            total_tasks = len(df_reports)
            st.metric("Total Tasks", total_tasks)
            
        with col_b:
            done_tasks = len(df_reports[df_reports['is_done'] == 1])
            st.metric("Completed", done_tasks)
            
        with col_c:
            pending_tasks = total_tasks - done_tasks
            st.metric("Pending", pending_tasks)

        st.divider()
        
        st.subheader("📥 Export Data")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
    
            csv = df_reports.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Report as CSV",
                data=csv,
                file_name=f"task_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )
            
        with col_exp2:
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_reports.to_excel(writer, index=False, sheet_name='Tasks')
                
                st.download_button(
                    label="Download Report as Excel",
                    data=buffer.getvalue(),
                    file_name=f"task_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error("Excel export requires 'xlsxwriter' library.")


        st.divider()
        st.subheader("Visual Summary")
        if not df_reports.empty:

            status_counts = df_reports['is_done'].value_counts().rename({1: 'Done', 0: 'Pending'})
            st.bar_chart(status_counts)
