% 四阶龙格-库塔法求解洛伦兹方程并绘制动画
clc
clear all;
% 系统参数
s = 10;
r = 28;
b = 8/3;

% 初始条件
x0 = 5; 
y0 = 5;
z0 = 5;
h = 0.001;  % 步长
tspan = 0:h:50;  % 时间区间

% 初始化变量
n = length(tspan);  % 时间步数
x = zeros(n, 1);
y = zeros(n, 1);
z = zeros(n, 1);

x(1) = x0;
y(1) = y0;
z(1) = z0;

% 四阶龙格-库塔方法计算洛伦兹方程的解
for i = 1:n-1
    % 当前点的状态
    xi = x(i);
    yi = y(i);
    zi = z(i);
    
    % 计算四阶龙格-库塔法的k1, k2, k3, k4
    k1x = h * (-s*xi + s*yi);
    k1y = h * (-xi*zi + r*xi - yi);
    k1z = h * (xi*yi - b*zi);
    
    k2x = h * (-s*(xi + k1x/2) + s*(yi + k1y/2));
    k2y = h * (-(xi + k1x/2)*(zi + k1z/2) + r*(xi + k1x/2) - (yi + k1y/2));
    k2z = h * ((xi + k1x/2)*(yi + k1y/2) - b*(zi + k1z/2));
    
    k3x = h * (-s*(xi + k2x/2) + s*(yi + k2y/2));
    k3y = h * (-(xi + k2x/2)*(zi + k2z/2) + r*(xi + k2x/2) - (yi + k2y/2));
    k3z = h * ((xi + k2x/2)*(yi + k2y/2) - b*(zi + k2z/2));
    
    k4x = h * (-s*(xi + k3x) + s*(yi + k3y));
    k4y = h * (-(xi + k3x)*(zi + k3z) + r*(xi + k3x) - (yi + k3y));
    k4z = h * ((xi + k3x)*(yi + k3y) - b*(zi + k3z));
    
    % 更新 x, y, z
    x(i+1) = xi + (k1x + 2*k2x + 2*k3x + k4x)/6;
    y(i+1) = yi + (k1y + 2*k2y + 2*k3y + k4y)/6;
    z(i+1) = zi + (k1z + 2*k2z + 2*k3z + k4z)/6;
end

% 创建动画
figure;
axis tight;
grid on;
xlabel('X');
ylabel('Y');
zlabel('Z');
title('洛伦兹吸引子动画');

% 循环绘制轨迹的每一步
for i = 1:n
    plot3(x(1:i), y(1:i), z(1:i), 'r', 'LineWidth', 1.5);
    drawnow;  % 更新图形
    pause(0.01);  % 设置动画的播放速度
end

