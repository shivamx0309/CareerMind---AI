
import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import Sidebar from '../components/navigation/Sidebar'
import Topbar from '../components/navigation/Topbar'

export default function DashboardLayout() {
    const [collapsed, setCollapsed] = useState(false)
    const [mobileOpen, setMobileOpen] = useState(false)

    return (
        <div className="dashboard-layout">

            <Sidebar
                collapsed={collapsed}
                setCollapsed={setCollapsed}
                mobileOpen={mobileOpen}
                setMobileOpen={setMobileOpen}
            />

            <div className="dashboard-main">
                <Topbar
                    onMenuClick={() => setMobileOpen(true)}
                />

                <main className="dashboard-content">
                    <Outlet />
                </main>
            </div>

        </div>
    )
}
