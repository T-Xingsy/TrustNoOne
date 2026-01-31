// 页面数据更新函数
function updatePageWithProjectData(projectName) {
    const project = getProjectData(projectName);
    if (!project) {
        console.error('Project not found:', projectName);
        return;
    }

    // 更新页面标题
    document.title = `${projectName} - 画饼指数 ${project.score} | 画饼粉碎机`;

    // 更新项目名称
    document.querySelectorAll('.project-name').forEach(el => {
        el.textContent = projectName;
    });

    // 更新项目徽章
    const badge = document.querySelector('.project-badge');
    if (badge) {
        const badgeText = project.riskLevel === 'high' ? '⚠ 高画饼风险' :
                         project.riskLevel === 'medium' ? '⚠ 中画饼风险' : '✓ 低风险';
        badge.textContent = badgeText;
        badge.className = `project-badge ${project.riskLevel}`;
    }

    // 更新 Twitter
    const twitterLink = document.querySelector('.project-meta .meta-value a[href*="twitter"], .project-meta .meta-value a[href="#"]');
    if (twitterLink) {
        twitterLink.textContent = project.twitter;
    }

    // 更新官网
    const websiteLinks = document.querySelectorAll('.project-meta .meta-value a');
    if (websiteLinks.length > 1) {
        websiteLinks[1].textContent = project.website;
    }

    // 更新合约地址
    const contractValue = document.querySelector('.meta-item:nth-child(3) .meta-value');
    if (contractValue) {
        const shortContract = project.contract.substring(0, 14) + '...' + project.contract.substring(project.contract.length - 4);
        contractValue.textContent = shortContract;
    }

    // 更新最后验证时间
    const lastVerified = document.querySelector('.meta-item:nth-child(4) .meta-value');
    if (lastVerified && project.timeline.length > 0) {
        lastVerified.textContent = project.timeline[0].date;
    }

    // 更新画饼指数
    const scoreValue = document.querySelector('.score-value');
    if (scoreValue) {
        scoreValue.textContent = project.score;
        scoreValue.className = `score-value ${project.riskLevel}`;
    }

    // 更新风险状态
    const scoreStatus = document.querySelector('.score-status');
    if (scoreStatus) {
        scoreStatus.textContent = project.riskLabel;
    }

    // 更新雷达图
    updateRadarChart(project.dimensions);

    // 更新五维参数说明
    updateDimensionsList(project.dimensions);

    // 更新承诺统计
    updatePromisesStats(project.promisesStats);

    // 更新时间线
    updateTimeline(project.timeline);
}

// 更新雷达图
function updateRadarChart(dimensions) {
    const radarCoords = calculateRadarCoordinates(dimensions);

    // 更新 polygon
    const polygon = document.querySelector('.radar-polygon');
    if (polygon) {
        polygon.setAttribute('points', radarCoords.pointsString);

        // 根据诚信分数设置颜色
        const integrityScore = dimensions.integrity.score;
        let color, fillColor;
        if (integrityScore < 50) {
            color = 'var(--color-danger)';
            fillColor = 'rgba(204, 51, 51, 0.25)';
        } else if (integrityScore < 70) {
            color = 'var(--color-warning)';
            fillColor = 'rgba(204, 170, 51, 0.25)';
        } else {
            color = 'var(--color-success)';
            fillColor = 'rgba(0, 255, 65, 0.25)';
        }
        polygon.setAttribute('stroke', color);
        polygon.setAttribute('fill', fillColor);
    }

    // 更新数据点
    const circles = document.querySelectorAll('.radar-point');
    const order = ['integrity', 'fairness', 'finance', 'momentum', 'development'];

    order.forEach((key, index) => {
        if (circles[index]) {
            const coord = radarCoords.coords[key];
            const score = dimensions[key].score;

            circles[index].setAttribute('cx', coord.x);
            circles[index].setAttribute('cy', coord.y);

            // 设置颜色
            let color;
            if (score < 50) {
                color = 'var(--color-danger)';
            } else if (score < 70) {
                color = 'var(--color-warning)';
            } else {
                color = 'var(--color-success)';
            }
            circles[index].setAttribute('fill', color);
        }
    });
}

// 更新五维参数说明
function updateDimensionsList(dimensions) {
    const dimensionRows = document.querySelectorAll('.dimension-row');
    const order = ['integrity', 'fairness', 'development', 'finance', 'momentum'];

    order.forEach((key, index) => {
        if (dimensionRows[index]) {
            const dim = dimensions[key];
            const row = dimensionRows[index];

            // 更新等级 class
            row.className = `dimension-row ${dim.level}`;

            // 更新分数
            const scoreEl = row.querySelector('.dimension-score-inline');
            if (scoreEl) {
                scoreEl.textContent = dim.score;
                scoreEl.className = `dimension-score-inline ${dim.level}`;
            }

            // 更新进度条
            const barFill = row.querySelector('.dimension-bar-fill-inline');
            if (barFill) {
                barFill.style.width = `${dim.score}%`;
                barFill.className = `dimension-bar-fill-inline ${dim.level}`;
            }

            // 更新说明
            const explanation = row.querySelector('.dimension-explanation');
            if (explanation) {
                explanation.textContent = dim.explanation;
            }
        }
    });
}

// 更新承诺统计
function updatePromisesStats(stats) {
    const filterButtons = document.querySelectorAll('.filter-button');
    if (filterButtons.length >= 4) {
        filterButtons[0].textContent = `全部 (${stats.total})`;
        filterButtons[1].textContent = `✅ 已兑现 (${stats.fulfilled})`;
        filterButtons[2].textContent = `❌ 未兑现 (${stats.unfulfilled})`;
        filterButtons[3].textContent = `❓ 无法验证 (${stats.unverifiable})`;
    }
}

// 更新时间线（使用安全的 DOM 方法）
function updateTimeline(timeline) {
    const timelineContainer = document.querySelector('.timeline');
    if (!timelineContainer) return;

    // 清空现有时间线
    timelineContainer.innerHTML = '';

    // 添加新的时间线项
    timeline.forEach(item => {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item verified';

        // 创建日期元素
        const dateEl = document.createElement('div');
        dateEl.className = 'timeline-date';
        dateEl.textContent = item.date;

        // 创建内容元素
        const contentEl = document.createElement('div');
        contentEl.className = 'timeline-content';
        contentEl.textContent = item.summary;

        // 创建分数容器
        const scoreContainer = document.createElement('div');
        scoreContainer.className = 'timeline-score';

        const scoreLabel = document.createElement('span');
        scoreLabel.textContent = '诚信分:';

        const scoreValue = document.createElement('span');
        scoreValue.className = 'timeline-score-value';
        scoreValue.textContent = item.integrityScore;

        const scoreColor = item.integrityScore < 50 ? 'var(--color-danger)' :
                          item.integrityScore < 70 ? 'var(--color-warning)' : 'var(--color-success)';
        scoreValue.style.color = scoreColor;

        scoreContainer.appendChild(scoreLabel);
        scoreContainer.appendChild(scoreValue);

        // 组装时间线项
        timelineItem.appendChild(dateEl);
        timelineItem.appendChild(contentEl);
        timelineItem.appendChild(scoreContainer);

        // 添加点击事件
        timelineItem.addEventListener('click', function() {
            const date = this.querySelector('.timeline-date').textContent;
            const score = this.querySelector('.timeline-score-value').textContent;
            showToast(`查看 ${date} 的历史版本（画饼指数: ${score}）`);
        });

        timelineContainer.appendChild(timelineItem);
    });
}

// Toast 提示函数
function showToast(message) {
    let toast = document.querySelector('.share-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'share-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
