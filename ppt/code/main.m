clc
clear all
sigma=10;
rho=28;
beta=8/3;
x_eq=6*sqrt(2);
y_eq=6*sqrt(2);
z_eq=27;

%生成线性矩阵
A1=generate_matrixA1(sigma,rho,z_eq,x_eq,y_eq,beta);

%获取变换特征
lambda=eig(A1);
[lambda1, a, b] = get_lambda_and_ab(A1);
P = transformation_matrixP(A1, lambda1, a, b)

T = 1000;
h = 0.01;

plot_lorenz_and_surface(P, lambda1, a, x_eq, y_eq, z_eq, T, h);











