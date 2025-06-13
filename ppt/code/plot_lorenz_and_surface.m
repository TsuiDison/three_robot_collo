function plot_lorenz_and_surface(P, lambda1, a, x_eq, y_eq, z_eq, T, h, x0 ,y0, z0)
    % 参数设置
    sigma = 10;
    rho = 28;
    beta = 8/3;

    % ====== 1. 生成曲面 F2(x, y, z_eq) ======
    [X, Y] = meshgrid(linspace(x_eq-20, x_eq+20, 100), linspace(y_eq-30, y_eq+30, 100));
    Z = z_eq * ones(size(X));
    
    XYZ = [X(:) - x_eq, Y(:) - y_eq, Z(:) - z_eq]';
    UVW = P \ XYZ;
    
    U = reshape(UVW(1, :), size(X));
    V = reshape(UVW(2, :), size(X));
    W = reshape(UVW(3, :), size(X));
    
    F2 = lambda1 * U.^2 + a * V.^2 + a * W.^2;

    % ====== 2. 计算洛伦兹轨迹 ======
    t = 0:h:T;
    N = length(t);
    x = zeros(1, N); y = zeros(1, N); z = zeros(1, N);
    x(1) = x0; y(1) = y0; z(1) = z0;

    f = @(x, y, z) [
        sigma * (y - x);
        x * (rho - z) - y;
        x * y - beta * z
    ];

    for i = 1:N-1
        k1 = h * f(x(i), y(i), z(i));
        k2 = h * f(x(i)+0.5*k1(1), y(i)+0.5*k1(2), z(i)+0.5*k1(3));
        k3 = h * f(x(i)+0.5*k2(1), y(i)+0.5*k2(2), z(i)+0.5*k2(3));
        k4 = h * f(x(i)+k3(1), y(i)+k3(2), z(i)+k3(3));
        x(i+1) = x(i) + (k1(1)+2*k2(1)+2*k3(1)+k4(1))/6;
        y(i+1) = y(i) + (k1(2)+2*k2(2)+2*k3(2)+k4(2))/6;
        z(i+1) = z(i) + (k1(3)+2*k2(3)+2*k3(3)+k4(3))/6;
    end

    % ====== 3. 绘图 ======
    figure;
    hold on;
    surf(X, Y, F2, 'EdgeColor', 'none', 'FaceAlpha', 0.6);
    plot3(x, y, z, 'r', 'LineWidth', 1.5);
    xlabel('x'); ylabel('y'); zlabel('z / F_2(x,y,z_{eq})');
    title('Lorenz Attractor over Surface F_2(x,y,z_{eq})');
    legend('F_2 Surface', 'Lorenz Trajectory');
    colormap turbo;
    view(45, 25);
    %限制一下z轴，不然太大了
    zlim([-20 60]);
    grid on;
end
