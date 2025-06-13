function equilibrium_points = lorenz_equilibrium(rho, beta)
    %根据方程参数输出平衡点
    if beta * (rho - 1) < 0
        warning('No real equilibrium points exist for the given parameters.');
        equilibrium_points = [];
        return;
    end
    equilibrium_points = [0, 0, 0];
    if beta * (rho - 1) >= 0
        sqrt_term = sqrt(beta * (rho - 1));
        equilibrium_points = [equilibrium_points; sqrt_term, sqrt_term, rho - 1];
        equilibrium_points = [equilibrium_points; -sqrt_term, -sqrt_term, rho - 1];
    end
end
