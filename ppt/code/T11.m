clc
clear all
% 初始条件
y0 = [1; 1; 1];  % 初始值
tspan = [0 50];   % 时间区间

% 使用 ode45 求解洛伦兹方程
[t, y] = ode45(@ydot, tspan, y0);

% 绘制三维轨迹
figure
plot3(y(:,1), y(:,2), y(:,3), 'LineWidth', 1.5);
xlabel('X');
ylabel('Y');
zlabel('Z');


function dydt = ydot(t, y)
    s = 10;
    r = 28;
    b = 8/3;
    dydt = zeros(3,1); % 初始化dydt为3x1的零向量
    
    dydt(1) = -s*y(1) + s*y(2);
    dydt(2) = -y(1)*y(3) + r*y(1) - y(2);
    dydt(3) = y(1)*y(2) - b*y(3);
end

