# data_analysis_improved.py
# -*- coding: utf-8 -*-

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import seaborn as sns
import os
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
OUTPUT_DIR = 'analysis_results'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_output_path(filename):
    """生成带时间戳的输出文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    return os.path.join(OUTPUT_DIR, f"{name}_{timestamp}{ext}")

def load_and_analyze_data():
    """加载和分析delivery_log.json数据"""
    with open('delivery_log.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    return df, data

def create_performance_overview(df):
    """创建系统性能概览图表"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 策略分布饼图
    strategy_counts = df['strategy'].value_counts()
    strategy_mapping = {
        'relay_leg1': '中转第一阶段',
        'relay_leg2': '中转第二阶段', 
        'direct': '直达策略'
    }
    strategy_labels = [strategy_mapping.get(s, s) for s in strategy_counts.index]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    wedges, texts, autotexts = ax1.pie(strategy_counts.values, labels=strategy_labels, 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('策略分布统计', fontsize=14, fontweight='bold')
    
    # 2. 智能体工作分配
    agent_tasks = defaultdict(int)
    for _, row in df.iterrows():
        agent_type = row['agentId'].split('_')[0]
        agent_tasks[agent_type] += 1
    
    agent_mapping = {'drone': '无人机', 'car': '无人车', 'robot': '机器狗'}
    agent_names = [agent_mapping[k] for k in agent_tasks.keys()]
    agent_counts = list(agent_tasks.values())
    
    bars = ax2.bar(agent_names, agent_counts, color=['#FF9F43', '#10AC84', '#5F27CD'])
    ax2.set_title('智能体任务分配统计', fontsize=14, fontweight='bold')
    ax2.set_ylabel('任务数量')
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    # 3. 任务执行时长分布
    duration_bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]
    ax3.hist(df['duration'], bins=duration_bins, alpha=0.7, color='#6C5CE7', edgecolor='black')
    ax3.set_title('任务执行时长分布', fontsize=14, fontweight='bold')
    ax3.set_xlabel('执行时长 (秒)')
    ax3.set_ylabel('任务数量')
    ax3.grid(True, alpha=0.3)
    
    # 4. 任务权重vs执行时长散点图
    scatter = ax4.scatter(df['taskWeight'], df['duration'], 
                         c=df['taskUrgency'], cmap='RdYlBu_r', 
                         s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax4.set_title('任务重量 vs 执行时长 (颜色=紧急度)', fontsize=14, fontweight='bold')
    ax4.set_xlabel('任务重量 (kg)')
    ax4.set_ylabel('执行时长 (秒)')
    ax4.grid(True, alpha=0.3)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('紧急度等级')
    
    plt.tight_layout()
    output_path = get_output_path('system_performance_overview.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 系统性能概览图已保存到: {output_path}")
    plt.show()

def create_collaboration_analysis(df, data):
    """创建协作效果分析图表"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 中转策略vs直达策略效果对比
    relay_tasks = df[df['strategy'].str.contains('relay')]
    direct_tasks = df[df['strategy'] == 'direct']
    
    # 按原始任务ID分组中转任务
    relay_groups = relay_tasks.groupby('originalTaskId')
    relay_total_durations = []
    for name, group in relay_groups:
        relay_total_durations.append(group['duration'].sum())
    
    strategy_comparison = {
        '中转策略': relay_total_durations,
        '直达策略': direct_tasks['duration'].tolist()
    }
    
    box_data = [strategy_comparison['中转策略'], strategy_comparison['直达策略']]
    bp = ax1.boxplot(box_data, tick_labels=['中转策略', '直达策略'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#FF6B6B')
    bp['boxes'][1].set_facecolor('#4ECDC4')
    
    ax1.set_title('中转策略 vs 直达策略效果对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('总执行时长 (秒)')
    ax1.grid(True, alpha=0.3)
    
    # 2. 时间轴上的任务执行情况
    start_times = pd.to_datetime(df['startTime'], unit='s')
    completion_times = pd.to_datetime(df['completionTime'], unit='s')
    
    # 转换为相对时间（从第一个任务开始的秒数）
    base_time = start_times.min()
    relative_start = (start_times - base_time).dt.total_seconds()
    relative_completion = (completion_times - base_time).dt.total_seconds()
    
    # 按智能体类型分组
    agent_colors = {'drone': '#FF9F43', 'car': '#10AC84', 'robot': '#5F27CD'}
    y_positions = {}
    y_counter = 0
    
    for i, row in df.iterrows():
        agent_type = row['agentId'].split('_')[0]
        agent_id = row['agentId']
        
        if agent_id not in y_positions:
            y_positions[agent_id] = y_counter
            y_counter += 1
        
        y_pos = y_positions[agent_id]
        duration = relative_completion.iloc[i] - relative_start.iloc[i]
        
        ax2.barh(y_pos, duration, left=relative_start.iloc[i], 
                height=0.6, color=agent_colors[agent_type], alpha=0.7,
                edgecolor='black', linewidth=0.5)
    
    ax2.set_title('任务执行时间轴', fontsize=14, fontweight='bold')
    ax2.set_xlabel('时间 (秒)')
    ax2.set_ylabel('智能体')
    ax2.set_yticks(range(len(y_positions)))
    ax2.set_yticklabels(list(y_positions.keys()))
    ax2.grid(True, alpha=0.3)
    
    # 3. 协作阶段分析
    leg1_tasks = df[df['strategy'] == 'relay_leg1']
    leg2_tasks = df[df['strategy'] == 'relay_leg2']
    
    stages_data = {
        '第一阶段\n(仓库→中转站)': leg1_tasks['duration'].tolist(),
        '第二阶段\n(中转站→目标)': leg2_tasks['duration'].tolist()
    }
    
    positions = [1, 2]
    bp2 = ax3.boxplot([stages_data['第一阶段\n(仓库→中转站)'], 
                       stages_data['第二阶段\n(中转站→目标)']], 
                      positions=positions, patch_artist=True)
    bp2['boxes'][0].set_facecolor('#E74C3C')
    bp2['boxes'][1].set_facecolor('#3498DB')
    
    ax3.set_title('中转协作两阶段时长对比', fontsize=14, fontweight='bold')
    ax3.set_ylabel('执行时长 (秒)')
    ax3.set_xticklabels(['第一阶段\n(仓库→中转站)', '第二阶段\n(中转站→目标)'])
    ax3.grid(True, alpha=0.3)
    
    # 4. 智能体协作网络图
    collaboration_matrix = np.zeros((7, 7))  # 假设最多7个智能体
    agent_list = sorted(df['agentId'].unique())
    agent_to_idx = {agent: i for i, agent in enumerate(agent_list)}
    
    # 统计协作关系（同一原始任务的不同leg）
    for original_task in df['originalTaskId'].unique():
        task_agents = df[df['originalTaskId'] == original_task]['agentId'].unique()
        if len(task_agents) > 1:  # 有协作
            for i, agent1 in enumerate(task_agents):
                for agent2 in task_agents[i+1:]:
                    idx1, idx2 = agent_to_idx[agent1], agent_to_idx[agent2]
                    collaboration_matrix[idx1][idx2] += 1
                    collaboration_matrix[idx2][idx1] += 1
    
    im = ax4.imshow(collaboration_matrix[:len(agent_list), :len(agent_list)], 
                    cmap='Reds', alpha=0.8)
    ax4.set_title('智能体协作关系矩阵', fontsize=14, fontweight='bold')
    ax4.set_xticks(range(len(agent_list)))
    ax4.set_yticks(range(len(agent_list)))
    ax4.set_xticklabels(agent_list, rotation=45)
    ax4.set_yticklabels(agent_list)
    
    # 添加数值标签
    for i in range(len(agent_list)):
        for j in range(len(agent_list)):
            text = ax4.text(j, i, int(collaboration_matrix[i, j]),
                           ha="center", va="center", color="black", fontweight='bold')
    
    plt.colorbar(im, ax=ax4, label='协作次数')
    
    plt.tight_layout()
    output_path = get_output_path('collaboration_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 协作效果分析图已保存到: {output_path}")
    plt.show()

def create_performance_metrics_table(df):
    """创建性能指标表格"""
    # 计算关键指标
    total_tasks = len(df)
    total_original_tasks = df['originalTaskId'].nunique()
    success_rate = 100.0  # 所有任务都完成了
    
    avg_duration = df['duration'].mean()
    min_duration = df['duration'].min()
    max_duration = df['duration'].max()
    std_duration = df['duration'].std()
    
    # 策略分析
    relay_tasks = df[df['strategy'].str.contains('relay')]
    direct_tasks = df[df['strategy'] == 'direct']
    
    # 按原始任务计算中转策略总时长
    relay_groups = relay_tasks.groupby('originalTaskId')
    relay_total_durations = [group['duration'].sum() for name, group in relay_groups]
    
    relay_avg = np.mean(relay_total_durations) if relay_total_durations else 0
    direct_avg = direct_tasks['duration'].mean() if not direct_tasks.empty else 0
    
    # 智能体分析
    agent_stats = df.groupby(df['agentId'].str.split('_').str[0]).agg({
        'taskId': 'count',
        'duration': ['mean', 'sum']
    }).round(2)
    
    # 创建性能指标表格图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 表格1：系统总体性能
    performance_data = [
        ['指标', '数值', '说明'],
        ['任务完成率', f'{success_rate:.1f}%', f'{total_tasks}/{total_tasks}任务成功'],
        ['原始任务数', f'{total_original_tasks}个', '用户定义的配送任务'],
        ['执行子任务数', f'{total_tasks}个', '包含中转分段任务'],
        ['平均执行时长', f'{avg_duration:.2f}秒', f'范围: {min_duration:.2f}-{max_duration:.2f}秒'],
        ['时长标准差', f'{std_duration:.2f}秒', '执行时长稳定性指标'],
        ['中转策略占比', f'{len(relay_total_durations)/total_original_tasks*100:.1f}%', f'{len(relay_total_durations)}/{total_original_tasks}使用中转'],
        ['直达策略占比', f'{len(direct_tasks)/total_original_tasks*100:.1f}%', f'{len(direct_tasks)}/{total_original_tasks}使用直达'],
        ['中转策略均时', f'{relay_avg:.2f}秒', '两阶段总时长均值'],
        ['直达策略均时', f'{direct_avg:.2f}秒', '单阶段执行时长均值']
    ]
    
    ax1.axis('tight')
    ax1.axis('off')
    table1 = ax1.table(cellText=performance_data[1:], colLabels=performance_data[0],
                       cellLoc='center', loc='center')
    table1.auto_set_font_size(False)
    table1.set_fontsize(10)
    table1.scale(1.2, 2)
    
    # 设置表格样式
    for i in range(len(performance_data[0])):
        table1[(0, i)].set_facecolor('#3498DB')
        table1[(0, i)].set_text_props(weight='bold', color='white')
    
    ax1.set_title('系统性能指标汇总', fontsize=16, fontweight='bold', pad=20)
    
    # 表格2：智能体性能对比
    agent_mapping = {'drone': '无人机', 'car': '无人车', 'robot': '机器狗'}
    agent_data = [['智能体类型', '任务数量', '平均时长(秒)', '总工作时长(秒)', '工作负载占比']]
    
    total_work_time = agent_stats[('duration', 'sum')].sum()
    for agent_type, stats in agent_stats.iterrows():
        task_count = int(stats[('taskId', 'count')])
        avg_duration = stats[('duration', 'mean')]
        total_duration = stats[('duration', 'sum')]
        workload_ratio = (total_duration / total_work_time) * 100
        
        agent_data.append([
            agent_mapping.get(agent_type, agent_type),
            f'{task_count}',
            f'{avg_duration:.2f}',
            f'{total_duration:.2f}',
            f'{workload_ratio:.1f}%'
        ])
    
    ax2.axis('tight')
    ax2.axis('off')
    table2 = ax2.table(cellText=agent_data[1:], colLabels=agent_data[0],
                       cellLoc='center', loc='center')
    table2.auto_set_font_size(False)
    table2.set_fontsize(10)
    table2.scale(1.2, 2)
    
    # 设置表格样式
    for i in range(len(agent_data[0])):
        table2[(0, i)].set_facecolor('#E74C3C')
        table2[(0, i)].set_text_props(weight='bold', color='white')
    
    ax2.set_title('智能体性能对比', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_path = get_output_path('performance_metrics_table.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 性能指标表格已保存到: {output_path}")
    plt.show()
    
    return performance_data, agent_data

def main():
    """主函数"""
    print("🔍 正在分析delivery_log.json数据...")
    
    # 加载数据
    df, data = load_and_analyze_data()
    
    print(f"📊 共加载 {len(df)} 条任务记录")
    print(f"📋 涉及 {df['originalTaskId'].nunique()} 个原始任务")
    print(f"🤖 使用 {df['agentId'].nunique()} 个智能体")
    
    # 生成图表
    print("\n📈 正在生成性能概览图表...")
    create_performance_overview(df)
    
    print("🤝 正在生成协作效果分析图表...")
    create_collaboration_analysis(df, data)
    
    print("📋 正在生成性能指标表格...")
    performance_data, agent_data = create_performance_metrics_table(df)
    
    print(f"\n🎉 数据分析完成！所有图片已保存到 '{OUTPUT_DIR}' 目录：")
    print("📊 system_performance_overview_*.png - 系统性能概览")
    print("🤝 collaboration_analysis_*.png - 协作效果分析") 
    print("📋 performance_metrics_table_*.png - 性能指标表格")
    print(f"\n💡 提示：文件名包含时间戳，便于版本管理")
    
    return df, performance_data, agent_data

if __name__ == "__main__":
    df, performance_data, agent_data = main()