function lorenz_rk4(sigma, rho, beta, x0, y0, z0, T, h)
%用于绘制给定方程、初值、步长以及时间范围的洛伦兹方程
    % 初始化
    t = 0:h:T; % 时间从 0 到 T，步长为 h
    N = length(t); % 时间步数
    
    % 初始化解
    x = zeros(1, N);
    y = zeros(1, N);
    z = zeros(1, N);
    
    % 初始条件
    x(1) = x0;
    y(1) = y0;
    z(1) = z0;
    
    % 洛伦兹方程的右侧
    f = @(x, y, z) [
        sigma * (y - x);                    % dx/dt
        x * (rho - z) - y;                  % dy/dt
        x * y - beta * z                    % dz/dt
    ];
    
    % 使用四阶龙格-库塔法进行迭代
    for i = 1:N-1
        % 当前时刻的值
        x_n = x(i);
        y_n = y(i);
        z_n = z(i);
        
        % 计算 k1, k2, k3, k4
        k1 = h * f(x_n, y_n, z_n);
        k2 = h * f(x_n + 0.5*k1(1), y_n + 0.5*k1(2), z_n + 0.5*k1(3));
        k3 = h * f(x_n + 0.5*k2(1), y_n + 0.5*k2(2), z_n + 0.5*k2(3));
        k4 = h * f(x_n + k3(1), y_n + k3(2), z_n + k3(3));
        
        % 更新下一步的解
        x(i+1) = x_n + (k1(1) + 2*k2(1) + 2*k3(1) + k4(1)) / 6;
        y(i+1) = y_n + (k1(2) + 2*k2(2) + 2*k3(2) + k4(2)) / 6;
        z(i+1) = z_n + (k1(3) + 2*k2(3) + 2*k3(3) + k4(3)) / 6;
    end
    
    % 绘制结果曲线
    figure;
    subplot(3, 1, 1);
    plot(t, x);
    title('x(t)');
    xlabel('Time');
    ylabel('x');
    
    subplot(3, 1, 2);
    plot(t, y);
    title('y(t)');
    xlabel('Time');
    ylabel('y');
    
    subplot(3, 1, 3);
    plot(t, z);
    title('z(t)');
    xlabel('Time');
    ylabel('z');
    
    % 绘制x, y, z的三维轨迹
    figure;
    plot3(x, y, z);
    title('Lorenz Attractor');
    xlabel('x');
    ylabel('y');
    zlabel('z');
end
