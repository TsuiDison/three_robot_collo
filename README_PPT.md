# PPT图片集成使用说明

## 数据分析可视化程序 - 独立图表版

我已经创建了一个新的数据分析程序 `data_analysis_separate.py`，它会生成独立的图表而非组合在一起的田字图。

### 🎯 **独立图表优势**

1. **更高清晰度** - 每个图表都是单独生成，不会因为空间限制而缩小
2. **灵活布局** - 可以根据需要选择和组合不同图表
3. **独立使用** - 可以单独提取某个图表用于其他文档
4. **聚焦细节** - 每个图表占据更大空间，可以展示更多细节

### 📊 **生成的独立图表**

1. **系统性能概览系列**：
   - `strategy_distribution_*.png` - 策略分布饼图
   - `agent_workload_*.png` - 智能体工作分配柱状图
   - `duration_distribution_*.png` - 任务执行时长分布直方图
   - `weight_duration_scatter_*.png` - 任务重量vs执行时长散点图

2. **协作效果分析系列**：
   - `strategy_comparison_*.png` - 中转策略vs直达策略箱线图
   - `task_timeline_*.png` - 任务执行时间轴
   - `relay_stages_comparison_*.png` - 中转两阶段时长对比
   - `collaboration_matrix_*.png` - 智能体协作关系矩阵

3. **性能指标表格**：
   - `system_performance_table_*.png` - 系统性能指标表格
   - `agent_performance_table_*.png` - 智能体性能对比表格

### 📝 **在PPT中使用独立图表的步骤**

修改 `main.tex` 文件中的可视化展示部分，将独立图表整合到PPT中。例如：

```latex
\subsection{系统可视化展示}

\begin{frame}{策略分布与智能体工作负载}
    \begin{columns}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/strategy_distribution_20241225_xxxxxx.png}
                \caption{策略分布饼图}
            \end{figure}
        \end{column}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/agent_workload_20241225_xxxxxx.png}
                \caption{智能体工作分配}
            \end{figure}
        \end{column}
    \end{columns}
\end{frame}

\begin{frame}{执行时长分析}
    \begin{columns}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/duration_distribution_20241225_xxxxxx.png}
                \caption{任务执行时长分布}
            \end{figure}
        \end{column}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/weight_duration_scatter_20241225_xxxxxx.png}
                \caption{任务重量vs执行时长关系}
            \end{figure}
        \end{column}
    \end{columns}
\end{frame}

\begin{frame}{协作策略分析}
    \begin{columns}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/strategy_comparison_20241225_xxxxxx.png}
                \caption{中转vs直达策略对比}
            \end{figure}
        \end{column}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/relay_stages_comparison_20241225_xxxxxx.png}
                \caption{中转两阶段对比}
            \end{figure}
        \end{column}
    \end{columns}
\end{frame}

\begin{frame}{智能体协作网络}
    \begin{columns}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/task_timeline_20241225_xxxxxx.png}
                \caption{任务执行时间轴}
            \end{figure}
        \end{column}
        \begin{column}{0.5\textwidth}
            \begin{figure}[htbp]
                \centering
                \includegraphics[width=\textwidth]{analysis_results/collaboration_matrix_20241225_xxxxxx.png}
                \caption{智能体协作关系矩阵}
            \end{figure}
        \end{column}
    \end{columns}
\end{frame}

\begin{frame}{性能指标分析}
    \begin{figure}[htbp]
        \centering
        \includegraphics[width=0.8\textwidth]{analysis_results/system_performance_table_20241225_xxxxxx.png}
        \caption{系统性能指标汇总}
    \end{figure}
    \begin{figure}[htbp]
        \centering
        \includegraphics[width=0.8\textwidth]{analysis_results/agent_performance_table_20241225_xxxxxx.png}
        \caption{智能体性能对比}
    \end{figure}
\end{frame}
```

**注意**：将文件名中的 `20241225_xxxxxx` 替换为实际生成的时间戳

### 🔧 **使用方法**

1. **运行独立图表生成程序**:
   ```bash
   python data_analysis_separate.py
   ```

2. **图片存储位置**：所有图表会保存在 `analysis_results` 目录下：
   ```
   analysis_results/
   ├── strategy_distribution_20241225_*.png
   ├── agent_workload_20241225_*.png
   ├── duration_distribution_20241225_*.png
   ├── weight_duration_scatter_20241225_*.png
   ├── strategy_comparison_20241225_*.png
   ├── task_timeline_20241225_*.png
   ├── relay_stages_comparison_20241225_*.png
   ├── collaboration_matrix_20241225_*.png
   ├── system_performance_table_20241225_*.png
   └── agent_performance_table_20241225_*.png
   ```

3. **将图片复制到PPT目录**：
   ```bash
   # 确保PPT目录中有analysis_results文件夹
   mkdir -p ppt/analysis_results
   
   # 复制所有生成的图片
   cp analysis_results/*.png ppt/analysis_results/
   ```

4. **编译LaTeX PPT**：
   ```bash
   cd ppt
   xelatex main.tex
   ```

### 📊 **增强后的PPT结构**

使用独立图表后，您的PPT可以包含更多详细的数据可视化页面：

- **Slide 1**: 标题页
- **Slide 2**: 目录
- **Section 1**: 系统概述（2 slides）
- **Section 2**: 建模思路（6 slides）
- **Section 3**: 模型测试
  - **测试场景设计** (1 slide)
  - **策略分布与工作负载** (1 slide)
  - **执行时长分析** (1 slide)
  - **协作策略分析** (1 slide)
  - **智能体协作网络** (1 slide)
  - **性能指标分析** (1 slide)
- **Section 4**: 总结与展望（1 slide）

通过这些独立的、高清晰度的图表，您可以更加细致地展示系统的各项性能特点，让PPT的展示效果更加专业、清晰！