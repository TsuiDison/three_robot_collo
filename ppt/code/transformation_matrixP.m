function P = transformation_matrixP(A, lambda1, a, b)
    % 输入：3x3矩阵 A 以及 lambda1, a, b
    % 输出：变换矩阵 P，使得 P*A*inv(P) = diag(lambda1, a+bi, a-bi) 的相似形式
    
    % Step 1: 求特征值和特征向量
    [V, D] = eig(A);
    
    % Step 2: 找到对应 lambda1 的实特征向量
    idx1 = find(abs(diag(D) - lambda1) < 1e-6);
    v1 = V(:, idx1);
    
    % Step 3: 找到复共轭对的特征值对应的特征向量
    idx2 = find(abs(diag(D) - (a + 1i*b)) < 1e-6);
    v2_complex = V(:, idx2);
    
    % Step 4: 构造实基底（使用实部和虚部）
    v2 = real(v2_complex);
    v3 = imag(v2_complex);
    
    % Step 5: 构造 P
    P = [v1, v2, v3];
end
