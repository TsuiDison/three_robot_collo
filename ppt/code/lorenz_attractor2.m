function lorenz_attractor2()
    % 初始化参数
    sigma = 10;     % Prandtl数
    rho = 28;       % Rayleigh数
    beta = 8/3;     % 几何参数
    h = 0.01;       % 步长
    T = 50;         % 总时间
    y0 = [5;5;5];   % 初始条件
    
    % 动画控制标志
    isRunning = false;
    
    % 创建图形窗口
    fig = figure('Position', [100 100 1000 750], 'Name', 'Lorenz Attractor Controller');
    ax = axes('Parent', fig, 'Position', [0.1 0.35 0.8 0.6]);
    grid on; view(ax, [30 20]); rotate3d on;
    
    % 初始化控件句柄
    sigmaText = [];
    rhoText = [];
    betaText = [];
    
    % 动画控制按钮
    uicontrol('Style','pushbutton','String','▶','Position',[20 20 50 30],...
        'Callback',@(src,event)startAnimation);
    uicontrol('Style','pushbutton','String','Clear','Position',[20 60 50 30],...
        'Callback',@clearTrail, 'ForegroundColor',[0.9 0 0]);
    % 添加Stop按钮
    uicontrol('Style','pushbutton','String','Stop','Position',[20 100 50 30],...
        'Callback',@(src,event)stopAnimation, 'ForegroundColor',[0.9 0 0]);
    
    % 创建参数调节滑块
    createControls(fig);
    
    % 初始化动画对象
    hold(ax, 'on');
    trail = animatedline(ax, 'MaximumNumPoints',1000000, 'Color',[0.5 0.5 0.5]);
    head = scatter3(ax, nan, nan, nan, 'filled', 'MarkerFaceColor','r');
    hold(ax, 'off');
    
    % 控件创建函数
    function createControls(fig)
        % 统一参数
        sliderWidth = 120;
        textWidth = 80;
        verticalSpacing = 40;
        
        % Sigma控件组
        uicontrol('Parent',fig,'Style','text','Position',[100 verticalSpacing+30 textWidth 20],...
            'String','Sigma ','HorizontalAlignment','center');
        uicontrol('Parent',fig,'Style','slider','Position',[100 verticalSpacing sliderWidth 20],...
            'Min',1,'Max',100,'Value',sigma,...
            'Callback',@(src,~)updateParameter(src.Value, 'sigma'));
        sigmaText = uicontrol('Parent',fig,'Style','text','Position',[100+sliderWidth+10 verticalSpacing textWidth 20],...
            'String',num2str(sigma,'%.1f'),'BackgroundColor',[0.9 0.9 0.9]);
        
        % Rho控件组
        uicontrol('Parent',fig,'Style','text','Position',[100+sliderWidth+textWidth+30 verticalSpacing+30 textWidth 20],...
            'String','Rho ','HorizontalAlignment','center');
        uicontrol('Parent',fig,'Style','slider','Position',[100+sliderWidth+textWidth+30 verticalSpacing sliderWidth 20],...
            'Min',0.1,'Max',100,'Value',rho,...
            'Callback',@(src,~)updateParameter(src.Value, 'rho'));
        rhoText = uicontrol('Parent',fig,'Style','text','Position',[100+1.6*(sliderWidth+textWidth+30)-10 verticalSpacing textWidth 20],...
            'String',num2str(rho,'%.1f'),'BackgroundColor',[0.9 0.9 0.9]);
        
        % Beta控件组
        uicontrol('Parent',fig,'Style','text','Position',[100+2*(sliderWidth+textWidth+30) verticalSpacing+30 textWidth 20],...
            'String','Beta ','HorizontalAlignment','center');
        uicontrol('Parent',fig,'Style','slider','Position',[100+2*(sliderWidth+textWidth+30) verticalSpacing sliderWidth 20],...
            'Min',0.1,'Max',50,'Value',beta,...
            'Callback',@(src,~)updateParameter(src.Value, 'beta'));
        betaText = uicontrol('Parent',fig,'Style','text','Position',[100+2.7*(sliderWidth+textWidth+30)-20 verticalSpacing textWidth 20],...
            'String',num2str(beta,'%.2f'),'BackgroundColor',[0.9 0.9 0.9]);
    end

    % 参数更新函数
    function updateParameter(value, param)
        switch param
            case 'sigma'
                sigma = value;
                set(sigmaText, 'String', num2str(value,'%.1f'));
            case 'rho'
                rho = value;
                set(rhoText, 'String', num2str(value,'%.1f'));
            case 'beta'
                beta = value;
                set(betaText, 'String', num2str(value,'%.2f'));
        end
        updatePlot();
    end

    % 更新轨迹函数
    function updatePlot()
        % 计算新轨迹
        tspan = 0:h:T;
        Y = rk4(@lorenz_eq, tspan, y0, h);
        
        % 存储轨迹到figure属性
        set(fig, 'UserData', Y);
    end

   function clearTrail(~,~)
        % 清空轨迹线
        clearpoints(trail);
        % 重置头部标记
        set(head, 'XData',nan, 'YData',nan, 'ZData',nan);
        % 清空存储数据
        set(fig, 'UserData', []);
        drawnow;
   end

    % 动画启动函数
    function startAnimation(~,~)
        % 如果正在运行则直接返回
        if isRunning
            return;
        end
        isRunning = true;
        
        % 获取最新轨迹数据
        updatePlot();
        Y = get(fig, 'UserData');
        
        % 动画参数设置
        frameDelay = 0.001; % 帧间隔时间
        batchSize = 10;    % 每帧绘制点数
        
        % 逐帧绘制
        for k = 1:batchSize:size(Y,1)
            % 检查停止标志
            if ~isRunning
                break;
            end
            
            % 更新轨迹和头部
            range = k:min(k+batchSize-1, size(Y,1));
            addpoints(trail, Y(range,1), Y(range,2), Y(range,3));
            set(head, 'XData',Y(k,1), 'YData',Y(k,2), 'ZData',Y(k,3));
            
            % 刷新图形并暂停
            drawnow limitrate
            pause(frameDelay);
            
            % 检查窗口有效性
            if ~isvalid(fig)
                isRunning = false;
                return; 
            end
        end
        isRunning = false;
    end

    % 停止动画函数
    function stopAnimation(~,~)
        isRunning = false;
    end

    % 洛伦兹方程定义
    function dy = lorenz_eq(~,y)
        dy = zeros(3,1);
        dy(1) = sigma*(y(2) - y(1));
        dy(2) = y(1)*(rho - y(3)) - y(2);
        dy(3) = y(1)*y(2) - beta*y(3);
    end

    % RK4算法实现
    function Y = rk4(ode, tspan, y0, h)
        n = length(tspan);
        Y = zeros(n, length(y0));
        Y(1,:) = y0';
        for i = 1:n-1
            t = tspan(i);
            y = Y(i,:)';
            k1 = h * ode(t, y);
            k2 = h * ode(t + h/2, y + k1/2);
            k3 = h * ode(t + h/2, y + k2/2);
            k4 = h * ode(t + h, y + k3);
            Y(i+1,:) = y + (k1 + 2*k2 + 2*k3 + k4)/6;
        end
    end
end