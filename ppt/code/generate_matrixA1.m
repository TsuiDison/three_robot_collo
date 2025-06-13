function A1 = generate_matrixA1(sigma, rho, z_eq, x_eq, y_eq, beta)
    % 生成矩阵 A1，输入参数为 sigma, rho, z_eq, x_eq, y_eq, beta
    A1 = [
        -sigma, sigma, 0;
        rho - z_eq, -1, -x_eq;
        y_eq, x_eq, -beta
    ];
end
