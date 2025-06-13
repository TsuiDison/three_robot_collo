function lorenz_symbol_consistency()
    % 参数设置
    s = 10; r = 28; b = 8/3;
    t_total = 70;
    epsilon = 1e-8;  % 初始扰动
    
    % 初始条件
    y0_1 = [5; 5; 5];
    y0_2 = y0_1 + [epsilon; 0; 0];
    
    % 计算两个轨迹的符号序列
    [symbols1, times1] = generate_symbol_sequence(y0_1, t_total);
    [symbols2, times2] = generate_symbol_sequence(y0_2, t_total);
    
    % 对齐符号序列时间
    min_len = min(length(symbols1), length(symbols2));
    symbols1 = symbols1(1:min_len);
    symbols2 = symbols2(1:min_len);
    times1 = times1(1:min_len);
    times2 = times2(1:min_len);
    
    % 找到第一个不同的符号
    mismatch_idx = find(symbols1 ~= symbols2, 1);
    
    % 可视化结果（单图布局）
    figure('Position', [100 100 800 400])
    
    % 符号序列可视化（全幅显示）
    hold on
    stairs(times1, symbols1, 'b', 'LineWidth', 1.5, 'DisplayName','轨迹1')
    stairs(times2, symbols2, 'r', 'LineWidth', 1.5, 'DisplayName','轨迹2')
    
    % 标记第一个不一致点
    if ~isempty(mismatch_idx)
        plot([times1(mismatch_idx), times2(mismatch_idx)],...
             [symbols1(mismatch_idx), symbols2(mismatch_idx)],...
             'ko', 'MarkerSize', 8, 'LineWidth', 2, 'DisplayName','分歧点')
        text(times1(mismatch_idx), 0.5,...
            sprintf('首次分歧: %.2f', times1(mismatch_idx)),...
            'FontSize', 10, 'HorizontalAlignment', 'center')
    end
    
    % 图形修饰
    ylim([-0.1 1.1])
    xlabel('时间','FontSize',11)
    ylabel('符号状态','FontSize',11)
    title('洛伦茨系统符号序列演化对比','FontSize',12)
    legend('Location','best')
    grid on
    box on
    
    % 控制台输出
    if isempty(mismatch_idx)
        fprintf('符号序列完全一致，长达 %.2f 时间单位\n', t_total);
    else
        fprintf('首次不一致时间: %.2f 时间单位\n', times1(mismatch_idx));
    end
end  % 主函数结束

% 子函数必须统一使用end
function [symbols, event_times] = generate_symbol_sequence(y0, t_total)
    options = odeset('Events', @z_crossing_event, 'RelTol', 1e-8, 'AbsTol', 1e-10);
    [~, Y, te, ye, ~] = ode45(@lorenz_eq, [0 t_total], y0, options);
    
    % 生成符号序列
    initial_x = Y(1,1);
    symbols = [initial_x < 0];  % 初始符号
    event_times = 0;            % 初始时间
    
    % 处理所有事件
    for i = 1:length(te)
        x_at_event = ye(i,1);
        symbols = [symbols; x_at_event < 0];
        event_times = [event_times; te(i)];
    end
end  % 子函数结束

function [value, isterminal, direction] = z_crossing_event(~, y)
    z_target = 27;
    value = y(3) - z_target;
    direction = -1;  % 只检测下降穿越
    isterminal = 0;
end  % 子函数结束

function dy = lorenz_eq(~, y)
    s = 10; r = 28; b = 8/3;
    dy = zeros(3,1);
    dy(1) = s*(y(2) - y(1));
    dy(2) = y(1)*(r - y(3)) - y(2);
    dy(3) = y(1)*y(2) - b*y(3);
end  % 子函数结束