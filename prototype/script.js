// 时迹 (TimeTrace) UI原型交互脚本

document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面
    initNavigation();
    initInteractions();
    updateCurrentTime();
    
    // 每秒更新时间
    setInterval(updateCurrentTime, 1000);
});

// 导航功能
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.page');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetPage = this.getAttribute('data-page');
            
            // 更新导航状态
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // 切换页面
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(targetPage).classList.add('active');
        });
    });
}

// 交互功能
function initInteractions() {
    // 模拟数据加载
    simulateDataLoading();

    // 表格行点击效果
    initTableInteractions();

    // 按钮点击效果
    initButtonInteractions();

    // 图表悬停效果
    initChartInteractions();

    // 视图切换功能
    initViewToggle();

    // 日历功能
    initCalendar();
}

// 模拟数据加载
function simulateDataLoading() {
    // 模拟统计数据更新
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(value => {
        const originalText = value.textContent;
        value.textContent = '加载中...';
        
        setTimeout(() => {
            value.textContent = originalText;
            value.style.animation = 'fadeIn 0.5s ease-in';
        }, Math.random() * 1000 + 500);
    });
}

// 表格交互
function initTableInteractions() {
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            // 移除其他行的选中状态
            tableRows.forEach(r => r.classList.remove('selected'));
            // 添加当前行的选中状态
            this.classList.add('selected');
        });
    });
    
    // 编辑按钮点击
    const editButtons = document.querySelectorAll('.btn-icon[title="编辑"]');
    editButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            showEditDialog();
        });
    });

    // 时间标记按钮点击
    const markButtons = document.querySelectorAll('.btn-icon[title="时间标记"]');
    markButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const row = this.closest('tr');
            const date = row.cells[0].textContent;
            showTimeMarking(date);
        });
    });
}

// 按钮交互
function initButtonInteractions() {
    // 新增记录按钮
    const addButton = document.querySelector('[data-action="add"]');
    if (addButton) {
        addButton.addEventListener('click', function() {
            showAddDialog();
        });
    }
    
    // 导出按钮
    const exportButton = document.querySelector('[data-action="export"]');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            simulateExport();
        });
    }
    
    // 保存设置按钮
    const saveButton = document.querySelector('.settings-actions .btn-primary');
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            saveSettings();
        });
    }
}

// 图表交互
function initChartInteractions() {
    // 图表点悬停效果
    const chartPoints = document.querySelectorAll('.chart-point');
    chartPoints.forEach(point => {
        point.addEventListener('mouseenter', function() {
            showTooltip(this, '8小时30分钟');
        });
        
        point.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
    
    // 柱状图悬停效果
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, index) => {
        bar.addEventListener('mouseenter', function() {
            const dataValue = this.getAttribute('data-value');
            showTooltip(this, dataValue || `${[7.5, 8.2, 7.8, 8.5, 8.0, 8.3, 7.2][index]}小时`);
        });

        bar.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

// 显示提示框
function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #303133;
        color: #fff;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 9999;
        pointer-events: none;
        white-space: nowrap;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
}

// 隐藏提示框
function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// 显示编辑对话框
function showEditDialog() {
    alert('编辑功能演示\n\n这里将打开编辑工时记录的对话框，用户可以修改上班时间、下班时间等信息。');
}

// 显示新增对话框
function showAddDialog() {
    alert('新增记录功能演示\n\n这里将打开新增工时记录的对话框，用户可以手动添加工时记录。');
}

// 模拟导出功能
function simulateExport() {
    const button = event.target.closest('.btn');
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 导出中...';
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
        alert('导出完成！\n\n工时数据已导出为CSV文件。');
    }, 2000);
}

// 保存设置
function saveSettings() {
    const button = event.target;
    const originalText = button.textContent;
    
    button.textContent = '保存中...';
    button.disabled = true;
    
    setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
        showNotification('设置保存成功！', 'success');
    }, 1000);
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#67c23a' : '#409eff'};
        color: #fff;
        padding: 12px 20px;
        border-radius: 4px;
        font-size: 14px;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 更新当前时间
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const footerLeft = document.querySelector('.footer-left span');
    if (footerLeft) {
        footerLeft.textContent = `最后更新时间: ${timeString}`;
    }
}

// 视图切换功能
function initViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const viewContents = document.querySelectorAll('.view-content');

    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetView = this.getAttribute('data-view');

            // 更新按钮状态
            viewButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // 切换视图内容
            viewContents.forEach(content => {
                content.classList.remove('active');
                if (content.classList.contains(`${targetView}-view`)) {
                    content.classList.add('active');
                }
            });

            // 如果切换到日历视图，生成日历
            if (targetView === 'calendar') {
                generateCalendar();
            }
        });
    });
}

// 日历功能
function initCalendar() {
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentDate.setMonth(currentDate.getMonth() - 1);
            generateCalendar();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentDate.setMonth(currentDate.getMonth() + 1);
            generateCalendar();
        });
    }
}

let currentDate = new Date();

// 生成日历
function generateCalendar() {
    const calendarDays = document.querySelector('.calendar-days');
    const currentMonth = document.getElementById('currentMonth');

    if (!calendarDays || !currentMonth) return;

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // 更新月份标题
    currentMonth.textContent = `${year}年${month + 1}月`;

    // 清空日历
    calendarDays.innerHTML = '';

    // 获取当月第一天和最后一天
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    // 生成42天（6周）
    for (let i = 0; i < 42; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);

        const dayElement = createCalendarDay(date, month);
        calendarDays.appendChild(dayElement);
    }
}

// 创建日历日期元素
function createCalendarDay(date, currentMonth) {
    const dayDiv = document.createElement('div');
    dayDiv.className = 'calendar-day';

    const isCurrentMonth = date.getMonth() === currentMonth;
    const isToday = date.toDateString() === new Date().toDateString();

    if (!isCurrentMonth) {
        dayDiv.classList.add('other-month');
    }

    if (isToday) {
        dayDiv.classList.add('today');
    }

    // 模拟工时数据
    const workData = getWorkDataForDate(date);
    if (workData && isCurrentMonth) {
        dayDiv.classList.add('has-work');
    }

    dayDiv.innerHTML = `
        <div class="day-number">${date.getDate()}</div>
        ${workData ? `<div class="day-work-time">${workData.hours}</div>` : ''}
        ${workData ? `<div class="day-status ${workData.status}"></div>` : ''}
    `;

    // 添加点击事件
    dayDiv.addEventListener('click', () => {
        if (isCurrentMonth) {
            editDateRecord(date);
        }
    });

    return dayDiv;
}

// 模拟获取日期工时数据
function getWorkDataForDate(date) {
    const day = date.getDay();
    const dateNum = date.getDate();

    // 周末不显示工时
    if (day === 0 || day === 6) return null;

    // 模拟一些工时数据
    const workHours = ['7.5h', '8h', '8.5h', '7h', '9h'];
    const statuses = ['normal', 'normal', 'normal', 'abnormal', 'manual'];

    return {
        hours: workHours[dateNum % workHours.length],
        status: statuses[dateNum % statuses.length]
    };
}

// 编辑日期记录
function editDateRecord(date) {
    const dateStr = date.toLocaleDateString('zh-CN');
    alert(`编辑 ${dateStr} 的工时记录\n\n这里将打开该日期的工时编辑对话框。`);
}

// 班次配置
function showShiftConfig() {
    alert('班次配置功能\n\n这里将打开班次配置对话框，用户可以：\n- 添加新的班次类型\n- 设置每个班次的工作时间\n- 配置班次轮换规则');
}

// 工作日历导入
function importWorkCalendar() {
    alert('导入工作日历\n\n支持导入以下格式：\n- iCal (.ics) 文件\n- CSV 格式的日期列表\n- 公司HR系统导出的工作日历');
}

// 显示日历编辑器
function showCalendarEditor() {
    alert('日历编辑器\n\n提供可视化界面编辑工作日历：\n- 标记法定节假日\n- 设置公司特殊工作日\n- 配置轮班安排\n- 批量设置工作制度');
}

// 添加特殊日期
function addSpecialDay() {
    alert('添加特殊日期\n\n可以添加：\n- 法定节假日调休\n- 公司特殊工作日\n- 个人请假日期\n- 出差工作日');
}

// 时间标记功能
function showTimeMarking(date) {
    alert(`时间标记功能\n\n为 ${date} 标记时间类型：\n- 实际工作时长\n- 摸鱼时长（休息、私事等）\n- 会议时长\n- 外出公干时长\n- 其他公务时长`);
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }

    .data-table tbody tr.selected {
        background-color: #ecf5ff !important;
    }

    .data-table tbody tr {
        transition: background-color 0.3s;
    }

    .chart-point {
        transition: transform 0.3s;
        cursor: pointer;
    }

    .chart-point:hover {
        transform: translate(-50%, 50%) scale(1.5);
    }

    .bar {
        transition: opacity 0.3s;
        cursor: pointer;
    }

    .bar:hover {
        opacity: 0.8;
    }

    .btn {
        transition: all 0.3s;
    }

    .btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
`;
document.head.appendChild(style);
