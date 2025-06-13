function [lambda_1, a, b] = get_lambda_and_ab(A)
%用来计算lambda_1、a和b
    % 使用 eig() 函数计算矩阵 A 的特征值
    lambda = eig(A);
    
    % 显示计算得到的特征值
    disp('特征值：');
    disp(lambda);
    
    % 查找实特征值 lambda_1 和复特征值的实部和虚部
    lambda_1 = lambda(imag(lambda) == 0); % 选择实特征值
    complex_eigs = lambda(imag(lambda) ~= 0); % 选择复特征值
    
    % 由于只有两个复特征值，所以从复数中提取实部和虚部
    a = real(complex_eigs(1));  % 实部 a
    b = imag(complex_eigs(1));  % 虚部 b
    
    % 打印结果
    fprintf('lambda_1: %.4f\n', lambda_1);
    fprintf('a: %.4f, b: %.4f\n', a, b);
end
