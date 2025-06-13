function lorenz_attractor()
    % 初始化参数
    sigma = 10;     % σ: Prandtl数
    rho = 28;       % ρ: Rayleigh数
    beta = 8/3;     % β: 几何参数
    h = 0.01;       % 步长
    T = 50;         % 总时间
    y0 = [5;5;5];   % 初始条件
    
    % 创建图形窗口
    fig = figure('Position', [100 100 1000 700], 'Name', 'Lorenz Attractor Controller');
    ax = axes('Parent', fig, 'Position', [0.1 0.3 0.8 0.65]);
    grid on; view(ax, [30 20]); rotate3d on;
    
    % 创建控件
    createControls(fig);
    
    % 初始绘图
    updatePlot();
    
    % 控件创建函数
    function createControls(fig)
        % 滑块布局参数
        paramPos = [
            80  220 300 20   % σ滑块
            80  190 300 20   % ρ滑块  
            80  160 300 20   % β滑块
            80  130 300 20]; % T滑块
        
        % 创建滑块控件
        uicontrol('Parent',fig, 'Style','slider', 'Tag','sigma',...
            'Min',1, 'Max',20, 'Value',sigma,...
            'Position',paramPos(1,:), 'Callback',@updatePlot);
        
        uicontrol('Parent',fig, 'Style','slider', 'Tag','rho',...
            'Min',0, 'Max',100, 'Value',rho,...
            'Position',paramPos(2,:), 'Callback',@updatePlot); 
        
        uicontrol('Parent',fig, 'Style','slider', 'Tag','beta',...
            'Min',0.1, 'Max',5, 'Value',beta,...
            'Position',paramPos(3,:), 'Callback',@updatePlot);
        
        uicontrol('Parent',fig, 'Style','slider', 'Tag','T',...
            'Min',10, 'Max',100, 'Value',T,...
            'Position',paramPos(4,:), 'Callback',@updatePlot);
        
        % 创建参数标签
        labelPos = [
            400 220 100 20
            400 190 100 20
            400 160 100 20
            400 130 100 20];
        
        tags = {'sigma', 'rho', 'beta', 'T'};
        for i=1:4
            uicontrol('Parent',fig, 'Style','text',...
                'Tag',[tags{i} '_label'],...  % 唯一标签
                'Position',labelPos(i,:),...
                'String',sprintf('%s = %.2f',tags{i},eval(tags{i})));
        end
    end

    % 更新函数
    function updatePlot(~,~)
        % 获取当前figure句柄
        fig = gcf();
        
        % 获取参数值
        sigma = findobj(fig, 'Tag','sigma').Value;
        rho = findobj(fig, 'Tag','rho').Value;
        beta = findobj(fig, 'Tag','beta').Value;
        T = findobj(fig, 'Tag','T').Value;
        
        % 更新参数标签
        tags = {'sigma', 'rho', 'beta', 'T'};
        for i=1:4
            label = findobj(fig, 'Tag',[tags{i} '_label']);
            set(label, 'String', sprintf('%s = %.2f',tags{i}, eval(tags{i})));
        end
        
        % 计算新轨迹
        tspan = 0:h:T;
        Y = rk4(@lorenz_eq, tspan, y0, h);
        
        % 更新图形
        if isempty(ax.Children)
            plot3(ax, Y(:,1), Y(:,2), Y(:,3));
        else
            set(ax.Children, 'XData',Y(:,1), 'YData',Y(:,2), 'ZData',Y(:,3));
        end
        title(ax, sprintf('σ=%.1f, ρ=%.1f, β=%.1f, T=%.0f',sigma,rho,beta,T));
        drawnow;
    end

    % 洛伦兹方程
    function dy = lorenz_eq(~,y)
        dy = [
            sigma*(y(2) - y(1));       % dx/dt
            y(1)*(rho - y(3)) - y(2);  % dy/dt
            y(1)*y(2) - beta*y(3)      % dz/dt
        ];
    end

    % RK4算法
    function Y = rk4(ode, tspan, y0, h)
        t = tspan(1):h:tspan(end);
        n = length(t);
        Y = zeros(n,3);
        Y(1,:) = y0';
        for i = 1:n-1
            k1 = h * ode(t(i), Y(i,:)');
            k2 = h * ode(t(i)+h/2, Y(i,:)' + k1/2);
            k3 = h * ode(t(i)+h/2, Y(i,:)' + k2/2);
            k4 = h * ode(t(i)+h, Y(i,:)' + k3);
            Y(i+1,:) = Y(i,:) + (k1 + 2*k2 + 2*k3 + k4)'/6;
        end
    end
end