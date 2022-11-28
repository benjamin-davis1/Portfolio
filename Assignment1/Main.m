close all
clc
%% Load environment
workspace = [-2 2 -2 2 -2 2];

ground = surf([-1.8,-1.8;1.8,1.8],[-2.5,1.8;-2.5,1.8],[0.01,0.01;0.01,0.01],'CData',imread('concrete.jpg'),'FaceColor','texturemap');

%% Load Objects
hold on
PlaceObject('table.ply', [0,0,0.5]);

hold on
PlaceObject('fireex.ply', [-0.5,1.2,1.2]);

hold on
PlaceObject('fence.ply', [1.2,0,0.8]);

hold on
PlaceObject('fence2.ply', [0,-1.75,0.8]);

hold on
PlaceObject('button.ply', [0,-1,1]);% hold on

camlight;
camlight;
%% Load LinearUR3
UR3 = LinearUR3(false);
%% Translate UR3
UR3.model.base = UR3.model.base * transl(0,1,0) * troty(pi/2);
UR3.model.animate(UR3.model.getpos);
%% Brick positions
% Initial brick positions
brickPos = [0.52  0 1;
         0.4 -0.1 1;
         0.5 -0.2 1;
         0.4 -0.3 1;
         0.5 -0.4 1;
         0.4 -0.5 1;
         0.5 -0.6 1;
         0.4 -0.7 1;
         0.5 -0.8 1];
% Brick placement in wall positions
wallPos = [ 0.1  0.5   1;
          0.0  0.5   1;
         -0.1  0.5   1;
          0.1  0.5  1.04;
          0.0  0.5  1.04;
         -0.1  0.5  1.04;
          0.1  0.5  1.08;
          0.0  0.5  1.08;
         -0.1  0.5  1.08];
%% Load Bricks
for i = 1:9
    hold on
    brick(i) = PlaceObject('HalfSizedRedGreenBrick.ply', brickPos(i,:));
end

%% Start building wall
q = zeros(1,9);
% Reset robot to initial pose
ResetRobot(UR3);
for i = 1:9
    %% Move to brick
    % Get the current End-effector pose
    UR3CurrPose = UR3.model.fkine(UR3.model.getpos());

    % Target brick pose w/ transl and trotx to turn into 4x4 homogenous matrix
    bLoc = transl(brickPos(i,1),brickPos(i,2),(brickPos(i,3)+0.165)) * trotx(pi);

    % Joint angles determined for robot end effector pose
    UR3ikcon = UR3.model.ikcon(bLoc,q);

    % Joint angle trajectory
    UR3traj = jtraj(q,UR3ikcon,25);
    
    % Iterates through joint trajectories
    for j = 1:size(UR3traj,1)
        hold on
        trajectory = UR3traj(j,:);
        UR3.model.animate(trajectory);
        UR3Fkine = UR3.model.fkine(UR3.model.getpos());
        drawnow();
        pause(0.05)
    end
    UR3Fkine

    %% Place brick
    q = UR3.model.getpos();

    UR3PlacePose = UR3.model.fkine(UR3.model.getpos());

    % Target brick pose w/ transl and trotx to turn into 4x4 homogenous matrix
    wLoc = transl(wallPos(i,1),wallPos(i,2),(wallPos(i,3)+0.165)) * trotx(pi);

    % Joint angles determined for robot end effector pose
    UR3ikcon = UR3.model.ikcon(wLoc,UR3.model.getpos());

    % Joint angle trajectory
    UR3traj = jtraj(q,UR3ikcon,25);

    % Delete brick from current location
    delete(brick(i));

    % Iterates through joint trajectories
    try
        for j = 1:size(UR3traj,1)
            hold on
            trajectory = UR3traj(j,:);
            UR3.model.animate(trajectory);
            UR3Fkine = UR3.model.fkine(UR3.model.getpos());
            drawnow();
            pause(0.05)
        end
    end
    UR3Fkine
    PlaceObject('HalfSizedRedGreenBrick.ply', wallPos(i,:));
    q = UR3.model.getpos();
end
%% Final Reset
% Reset robot to initial pose
ResetRobot(UR3);
%% Point cloud
stepRads = deg2rad(30);
qlim = UR3.model.qlim;


pointCloudSize = prod(floor((qlim(1:7,2) - qlim(1:7,1))/stepRads + 1));

pointCloud = zeros(pointCloudeSize,3);
counter = 1;
tic
for q1 = qlim(1,1):stepRads:qlim(1,2)
    for q2 = qlim(2,1):stepRads:qlim(2,2)
        for q3 = qlim(3,1):stepRads:qlim(3,2)
            for q4 = qlim(4,1):stepRads:qlim(4,2)
                for q5 = qlim(5,1):stepRads:qlim(5,2)
                    for q6 = qlim(6,1):stepRads:qlim(6,2)
                                % q7-q9 are gripper links and would only
                                % drastically increase calculation time
                                q7 = 0;
                                q8 = 0;
                                q9 = 0;
                                q = [q1,q2,q3,q4,q5,q6,q7,q8,q9];
                                tr = UR3.model.fkine(q);                        
                                pointCloud(counter,:) = tr(1:3,4)';
                                counter = counter + 1; 
                                if mod(counter/pointCloudSize * 100,1) == 0
                                    display(['After ',num2str(toc),' seconds, completed ',num2str(counter/pointCloudSize * 100),'% of poses']);
                                end
                    end
                end
            end
        end
    end
end
hold on
plot3(pointCloud(:,1),pointCloud(:,2),pointCloud(:,3),'r.');
%% Reset Robot
function ResetRobot(LinearUR3)
    %UR3.model.base = UR3.model.base * transl(0.5,0.5);
    LinearUR3.model.animate(LinearUR3.model.getpos)
    steps = 100;
    UR3traj = jtraj(LinearUR3.model.getpos,zeros([9,1]),steps);
    for i = 1:size(UR3traj,1)
        LinearUR3.model.animate(UR3traj(i,:));
        drawnow()
    end
end
%% Translate Robot
function translateRobot(LinearUR3, x, y, z)
    LinearUR3.model.base = LinearUR3.model.base * transl(x,y,z);
    LinearUR3.model.animate(LinearUR3.model.getpos)
end