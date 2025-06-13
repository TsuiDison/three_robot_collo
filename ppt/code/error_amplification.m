function error_amplification()
    s = 10; r = 28; b = 8/3;
    h = 0.0001;
    tspan = 0:h:20;
    epsilon = 1e-5;
    y0_1 = [5; 5; 5];
    y0_2 = y0_1 + [epsilon; 0; 0];
    speed_controller = struct('factor', 1);
    
    % 计算轨迹
    [Y1, Y2] = deal(rk4(@lorenz_eq,tspan,y0_1,h), rk4(@lorenz_eq,tspan,y0_2,h));
    
    %% 动画参数
    skip_step = 50;             % 每50步更新一帧
    max_points = 500;           % 轨迹显示点数
    base_fps = 60;              % 基准帧率
    
    % 预处理数据
    Y1_anim = Y1(1:skip_step:end, :);
    Y2_anim = Y2(1:skip_step:end, :);
    
    %% 创建双视图界面
    fig = figure('Position', [200 200 1200 600]);
    
    % 3D轨迹视图
    ax1 = subplot(1,2,1);
    view(ax1, [-20 20]);
    xlabel('x'); ylabel('y'); zlabel('z');
    title('Lorenz系统轨迹（实时更新）');
    grid on; hold on;
    
    % 2D误差视图
    ax2 = subplot(1,2,2);
    title('误差放大倍数演化');
    xlabel('时间'); ylabel('放大倍数（log）');
    set(ax2, 'YScale', 'log', 'FontSize',10);
    grid on; hold on;
    
    %% 初始化图形对象
    % 轨迹
    h1 = plot3(ax1, NaN, NaN, NaN, 'r-', 'LineWidth', 1.5);
    h2 = plot3(ax1, NaN, NaN, NaN, 'b-', 'LineWidth', 1.5);
    
    % 误差曲线
    error_plot = plot(ax2, NaN, NaN, 'k-', 'LineWidth', 1.5);
    legend(ax2, '误差放大倍数', 'Location','northwest')
    
    % 信息标签
    t_label = text(ax1, 0.02,0.95,0.9, 'Time: 0.00',...
                  'Units','normalized', 'FontSize',12, 'Color','k');
    
    % 速度控制滑块
    uicontrol('Style','text','Position',[50 10 100 20],...
             'String','播放速度倍数:','HorizontalAlignment','left');
    speed_slider = uicontrol('Style','slider',...
                            'Position',[160 10 300 20],...
                            'Min',0.1,'Max',100,'Value',1,...
                            'Callback',@update_speed);
    
    %% 动画循环
    frame_interval = 1/base_fps;
    error_data = struct('time', [], 'amp', []); % 误差存储结构体
    tic;
    
    for k = 1:length(Y1_anim)
        % 当前时间参数
        current_index = 1 + (k-1)*skip_step;
        current_time = tspan(current_index);
        
        %% 更新3D轨迹
        % 计算显示范围
        current_start = max(1, k - max_points + 1);
        current_indices = current_start:k;
        
        % 更新主轨迹
        set(h1, 'XData', Y1_anim(current_indices,1),...
                'YData', Y1_anim(current_indices,2),...
                'ZData', Y1_anim(current_indices,3));
        
        % 更新扰动轨迹
        set(h2, 'XData', Y2_anim(current_indices,1),...
                'YData', Y2_anim(current_indices,2),...
                'ZData', Y2_anim(current_indices,3));
        
        %% 计算并更新误差曲线
        % 计算当前误差
        current_error = norm(Y1(current_index,:) - Y2(current_index,:)) / epsilon;
        
        % 存储数据
        error_data.time(end+1) = current_time;
        error_data.amp(end+1) = current_error;
        
        % 更新误差曲线
        set(error_plot, 'XData', error_data.time, 'YData', error_data.amp);
        
        % 自动调整坐标范围
        xlim(ax2, [0 current_time+1])
        if current_error > 0
            ylim(ax2, [1 max(error_data.amp)*1.1])
        end
        
        %% 更新视图参数
        % 动态调整视角
        if mod(current_index, 5000) == 0
            view(ax1, [-20 + current_index/5000, 20]);
            axis(ax1, [-25 25 -30 30 0 50])
        end
        
        % 更新时间标签
        set(t_label,'String',sprintf('Time = %.1f  Speed: %.1fX',...
                    current_time, speed_controller.factor))
        
        %% 速度控制
        elapsed = toc;
        target_delay = frame_interval / speed_controller.factor;
        if elapsed < target_delay
            pause(max(target_delay - elapsed, 0.001));
        end
        drawnow limitrate
        tic;
    end

    %% 计算并打印特定时间点的误差放大因数
    index_10 = find(tspan >= 10, 1); % 精确查找时间索引
    index_20 = find(tspan >= 20, 1);
    
    error_10 = norm(Y1(index_10,:) - Y2(index_10,:)) / epsilon;
    error_20 = norm(Y1(index_20,:) - Y2(index_20,:)) / epsilon;
    
    fprintf('t=10时误差放大因数：%.2f\n', error_10);
    fprintf('t=20时误差放大因数：%.2f\n', error_20);

    %% 辅助函数
    function update_speed(src, ~)
        speed_controller.factor = src.Value;
    end
    function dy = lorenz_eq(t, y)
        dy = [s*(y(2)-y(1)); y(1)*(r-y(3))-y(2); y(1)*y(2)-b*y(3)];
    end
    
    function Y = rk4(ode, tspan, y0, h)
        t = tspan(1):h:tspan(end);
        Y = zeros(length(t), length(y0));
        Y(1,:) = y0';
        for i = 1:length(t)-1
            k1 = h * ode(t(i), Y(i,:)');
            k2 = h * ode(t(i)+h/2, Y(i,:)' + k1/2);
            k3 = h * ode(t(i)+h/2, Y(i,:)' + k2/2);
            k4 = h * ode(t(i)+h, Y(i,:)' + k3);
            Y(i+1,:) = Y(i,:) + (k1 + 2*k2 + 2*k3 + k4)'/6;
        end
    end
end